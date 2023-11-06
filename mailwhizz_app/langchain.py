from django.conf import settings
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import JinaChat

chat_llm = JinaChat(temperature=0, jinachat_api_key=settings.OPEN_AI_API_KEY)

# chat_llm = ChatOpenAI(
#     model_name=settings.OPEN_AI_CHAT_MODEL, 
#     openai_api_key=settings.OPEN_AI_API_KEY, 
#     temperature=0.8, # Controls the randomness of responses (lower values make it more focused)                        
#     model_kwargs = {                                    
#         "top_p": 0.9,              # Top-p sampling to ensure the generated text is diverse and creative
#         "frequency_penalty": 0.2,  # Encourage the model to produce less common words and phrases
#         "presence_penalty": 0.2,   # Encourage the model to be less repetitive                                                                 
#     }
# )  



class Assistant():  
    def extract_tasks_from_email(email_body):            
        # messages = [
        #     SystemMessage(
        #         content="You are a helpful assistant who extracts tasks required or key points from an email. The tasks/key points you extract MUST be a string separated by a comma with the task title and task category which can either: be high priority, Deadline, Critical, or Urgent. Tasks should be in format:  task title here - task category here. For example:- Submit financial report - Deadline, Call Mr. John - Urgent. DO NOT use this examples to generate the tasks / key points!"
        #     ),
        #     HumanMessage(content=f"""Generate tasks from the following email body. Adhere to the instructions given above.
        #                 **************************
        #                 {email_body}
        #                 **************************
        #                 """),
        # ]

        # results = chat_llm(messages)   

        # results = """
        # Tasks:

        # 1. Informing of weekly meeting - high priority.
        # 2. Weekly meeting - deadline.

        # Please let me know if you need further assistance.
        # """

        # list_x = results.replace("\n","").split('. ')
        # print("****************")        
        # for x in list_x:
        #     if "-" in x:
        #         print(f"->{x}")                
        # print("****************")

        task_list = [
            {"task":"Informing of weekly meeting", "category": "High Priority"},
            {"task":"Weekly meeting", "category": "Deadline"}
        ]
        return task_list