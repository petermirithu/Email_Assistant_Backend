import json
from django.conf import settings
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI


class Assistant():  
    def modelConfig(temperature=0):
        chat_llm = ChatOpenAI(
            model_name=settings.OPEN_AI_CHAT_MODEL,         
            openai_api_key=settings.OPEN_AI_API_KEY, 
            temperature=temperature, # Controls the randomness of responses (lower values make it more focused)                        
            model_kwargs = {                                    
                "top_p": 0.9,              # Top-p sampling to ensure the generated text is diverse and creative
                "frequency_penalty": 0.2,  # Encourage the model to produce less common words and phrases
                "presence_penalty": 0.2,   # Encourage the model to be less repetitive                                                                 
            }
        ) 
        return chat_llm

    def extract_tasks_from_email(ai_payload):                                                   
        schema = """
            [
                {
                    "task_title": "string",
                    "task_category": "string",                    
                },
                {
                    "task_title": "string",
                    "task_category": "string",
                }
            ]
        """
        chat_llm = Assistant.modelConfig(0)

        task_list = []

        for item in ai_payload:
            if item["type"] == "email":                
                messages = [
                    SystemMessage(
                        content=f"You are a helpful assistant who extracts tasks required or key points from an email. Your response MUST be an array of objects with fields task_title and task_category which can either be: High Priority, Deadline, Critical, Reminder or Urgent. Do not add any text outside the schema provided. If there are no tasks, return only\n[]\n\nIf there are tasks, your reponse MUST Use the schema:-\n{schema}"
                    ),
                    HumanMessage(content=f"""Generate tasks from the following email body. Adhere to the instructions given above.
                                **************************
                                {item["mail"]}
                                **************************
                                """),
                ]            
        
                email_results = chat_llm(messages).content        

                if "[]" in email_results:
                    pass
                elif email_results[0] == "[" and email_results[len(email_results)-1] == "]":
                    task_list = json.loads(email_results)
                    for item in task_list:
                        item["belongs_to"] = "email"
            else:
                if len(item["attachments"])>0:
                    for attachment in item["attachments"]:
                        messages = [
                            SystemMessage(
                                content=f"You are a helpful assistant who extracts tasks required or key points from an email. Your response MUST be an array of objects with fields task_title and task_category which can either be: High Priority, Deadline, Critical, Reminder or Urgent. Do not add any text outside the schema provided. If there are no tasks, return only\n[]\n\nIf there are tasks, your reponse MUST Use the schema:-\n{schema}"
                            ),
                            HumanMessage(content=f"""Generate tasks from the following email body. Adhere to the instructions given above.
                                        **************************
                                        {attachment["fileText"]}
                                        **************************
                                        """),
                        ]            
                
                        attachment_results = chat_llm(messages).content        

                        if "[]" in attachment_results:
                            pass
                        elif attachment_results[0] == "[" and attachment_results[len(attachment_results)-1] == "]":
                            task_list_v2 = json.loads(attachment_results)
                            for item in task_list_v2:
                                item["belongs_to"] = "attachment"
                                task_list.append(item)

        return task_list
    
    def generate_reply_suggestion_from_mail(text_to_process, option):
        format_instruction = ""
        if option == "attachment":
           format_instruction = "Your response should be in html format! Utilize html tags such as p tags to show paragraphs and other html elements to make the reply beautiful. Do not add any additional text outside the body. DO not type html anywhere!"

        messages = [
            SystemMessage(
                content=f"You are a helpful assistant who generates reply suggestions based on provided text. DO NOT include the subject to the reply. Just generate the body of the reply only! {format_instruction}."
            ),
            HumanMessage(content=f"""Generate a reply to the following email body. Follow the instructions given above! Do NOT return the same text given below. Generate your own reply suggestion based on the text provided.
                        **************************
                        {text_to_process}
                        **************************
                        """),
        ]
        
        chat_llm = Assistant.modelConfig(0.8)
        results = chat_llm(messages).content
        
        return results          

    def generate_summary_from_mail(email_body):
        messages = [
            SystemMessage(
                content="You are a helpful assistant who generates a summary from the text provided. Your response should be in html format! Utilize html tags such as p tags to show paragraphs and other html elements to make the summary beautiful. DO not type html anywhere!"
            ),
            HumanMessage(content=f"""Generate a summary from the following text. Follow the instructions given above! Do NOT return the same text given below. Generate your own summary that is brief and straight to the point based on the text provided.
                        **************************
                        {email_body}
                        **************************
                        """),
        ]
        
        chat_llm = Assistant.modelConfig(0.8)    
        results = chat_llm(messages).content
        
        return results 
