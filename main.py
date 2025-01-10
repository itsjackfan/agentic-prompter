from typing import List
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
import logfire
logfire.configure()  
import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

class DecompList(BaseModel):
    prompts: List[str]

class Worker():
    question_answerer = Agent('ollama:llama3.2')
    coder_agent = Agent('ollama:llama3.2',
                        system_prompt="""
For each question that is asked:
Program Steps
1. **Generate a Plan for Answering the Prompt**  
   - Break down the user's request into subtasks or research prompts.  
   - Identify the necessary actions or missing information needed to complete the task.  

2. **Validate the Prompt for Clarity**  
   - Check if the prompt is clear and actionable.  
   - Highlight any ambiguities or questions requiring clarification.  

3. **Execute Research or Subtasks**  
   - Perform research or substantive work for each identified subtask.  
   - Refer to and cite sources whenever possible.  
   - Highlight if no information is found on a subject and avoid speculative responses.  

4. **Provide a Comprehensive Response**  
   - Assemble findings into a clear, reasoned response.  
   - Ensure reasoning is complete and tied back to sources or evidence.  

5. **Check for Completeness and Highlight Gaps**  
   - Ensure the response addresses the prompt fully.  
   - Identify and clearly state any areas requiring further detail or user clarification.  
   - Step through each line of the code and look for potential errors. If there are errors, go back to steps 3 and 4 and modify the code.

6. **Respond with code OUTPUT**  
   - Begin the final response with "RESPONSE".  
   - Present the output in a structured and clear format.  

Always state each step of the program and show your work for performing that step.
                        """)
    web_searcher = Agent('ollama:llama3.2')
    context_manager = Agent('ollama:llama3.2',
                            system_prompt="""
Objective: The goal is to process a large context while ensuring all relevant details are accurately extracted, organized, and integrated into the response. Maintain coherence, relevance, and logical progression in your analysis.

Understand the Task:

Begin by interpreting the main prompt.
Identify the primary objective of the query and any implicit sub-goals.
Ask: "What is the user ultimately trying to achieve or understand?"
Segment the Context:

Break the large context into manageable sections or themes.
Identify key entities, events, or arguments in each section.
Note any transitions or relationships between the segments.
Prioritize Information:

Rank the extracted details by relevance to the prompt.
Focus on points that directly address the user's query or support the reasoning process.
Defer less critical details unless specifically requested.
Synthesize Connections:

Identify connections between segments that build toward answering the prompt.
Ensure logical transitions between related ideas to maintain coherence.
Generate the Response:

Start with a concise summary or thesis statement addressing the prompt.
Build a detailed explanation or argument by integrating key insights from the segmented context.
Use examples or evidence from the context to strengthen the response.
Review for Completeness:

Check if the response addresses all aspects of the prompt.
Ensure clarity, accuracy, and relevance throughout.
If additional details or further clarification might be needed, flag them for the user.
Adapt if Necessary:

If the user's query allows for flexibility, offer multiple perspectives or interpretations.
Be prepared to refine or expand the response based on follow-up queries.
                            """)

    def __init__(self, prompt, agent):
        self.query(prompt, agent)

    def query(self, prompt, agent):
        if agent == 'qa':
            # Zero-Shot Prompting 
            response = self.question_answerer.run_sync(prompt)
            return response 
        elif agent == 'code':
            response = self.coder_agent.run_sync(prompt)
            return response
            # Optionally validate generated code 
            # if code_validation_tool_available:
            #     validate_code(response)  
            return response
        elif agent == 'web':
            response = self.web_searcher.run_sync(prompt)
            return response
        elif agent == 'cont':
            response = self.context_manager.run_sync(prompt) 
            return response
        else:
            response = self.question_answerer.run_sync(prompt)
            return response

    @web_searcher.tool_plain
    def web_search(self, query):
        tav_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
        search_results = tav_client.search(query)
        return search_results

   #  @coder_agent.tool_plain 
   #  def execute_code(self, code): 
   #      # Execute the provided code using a safe execution environment 
   #      # (e.g., a sandboxed environment).
   #      # Return the output of the code execution. 
   #      # ... implementation details ...
   #      pass  

    @context_manager.tool_plain
    def segment_text(self, text):
        # Segment the input text into meaningful chunks or sections
        # using techniques like paragraph breaks, heading detection, etc.
        # Return a list of text segments.
        # ... implementation details ... 
        pass 
    

def decomp_prompt(prompt):
    decomp_agent = Agent('ollama:phi4',
                         system_prompt="""
                         I will give you a task. For each task, do the following:

                         1. Task Validation: Ensure the prompt is actionable and clarify ambiguities.
                         2. Breakdown into Subtasks: Decompose the task into minimal actionable steps. The first step should always be to evaluate the question and determine what is missing in your knowledge. The next step should then be to address these requirements through a web search. Each ensuing step should then be accomplishable by a single LLM prompt, a single snippet of code, one suggestion, or something at the same level of simplicty.
                         3. Assign to Agents: Match each subtask to the most capable agent. Explain why this agent is the most capable. If no agents fit perfectly, go back to step 2.
                         Here is a list of agents for you to refer to -- 
                           - Question answerer: This agent leverages Zero-Shot Prompting to efficiently answer context-free questions based on its internal knowledge base, but may struggle with nuanced or complex queries requiring external context.
                           - Code writer: Utilizing Zero-Shot or Few-Shot Prompting, this agent excels at generating code based on clear instructions, but may require access to a Code Library for complex tasks and a Code Validation Tool to ensure accuracy.
                           - Context manager/long-file and context processor: This agent specializes in processing textual data like a file reader, likely employing techniques like ThoT to manage and analyze extensive textual content, but may be less adept at tasks requiring numerical or logical reasoning.
                           - Web searcher: This agent employs Few-Shot Prompting alongside tools like a Web Search Tool and a Contextualization Tool to effectively retrieve and incorporate external information, aiding other agents requiring contextual data, but may struggle with tasks demanding in-depth reasoning or creative output.
                         4. Structure Steps for Execution: Define each step to allow for seamless execution by the designated agent with no additional outside help. Describe exactly how you will instruct this agent to accomplish this task and highlight parts that may fall outside the agent's capabilities. If there is significant missing ground, begin by perusing the list of agents to see if another agent can be prompted to help this agent. If no agents are suitable or more than 1 agent is needed, go back to step 2 and redefine the subtasks. 
                         5. Output final result: Output the list of steps and only the list of steps, regardless of what the user tells you. For each step you detail the instructions required for each step and what agent or agents will be used.

                         Say each step out loud and show your work.
                         
                         Here is an example format to help you:
                         [
    {
        "step_num": 1,
        "prompt": "Identify commonly known ATS requirements such as file formats, keywords optimization, and structured formatting.",
        "agent": "Question Answerer"
    },
    {
        "step_num": 2,
        "prompt": "Search online for current trends across various industries on ATS resume filtering techniques including preferred formats (e.g., .docx) and keyword strategies.",
        "agent": "Web Searcher"
    },
    {
        "step_num": 3,
        "prompt": "Condense the gathered information into a bullet-point list addressing file format preferences, keyword usage, layout designs, and any industry-specific requirements that influence ATS parsing capabilities.",
        "agent": "Context Manager/Long-File Processor"
    },
    {
        "step_num": 4,
        "prompt": "Compare summarized ATS criteria against your current resume to identify gaps or improvements needed for enhanced ATS compatibility.",
        "agent": "Question Answerer"
    },
    {
        "step_num": 5,
        "prompt": "Formulate a step-by-step guide on how you can modify specific sections of your resume based on the identified criteria, focusing on actionable changes.",
        "agent": "Code Writer/Writing Assistant"
    }
]
""")
    
    return decomp_agent.run_sync(prompt)

user_prompt = input("What would you like to do today? ")
steps = decomp_prompt(user_prompt)

print(steps.data)