from openai import OpenAI
import logging
from src.data_process import ProjectQueryInterface
from config import OPENAI_API_KEY

class ChatBotAssistant:
    """
    A chatbot assistant class that integrates OpenAI's GPT model and a project query interface to provide recommendations
    and detailed project information for crypto-related queries.
    """

    def __init__(self, gpt_api_key: str = OPENAI_API_KEY):
        """
        Initializes the ChatBotAssistant with access to the project database and OpenAI's GPT API.

        :param gpt_api_key: The API key for OpenAI's GPT model.
        """
        self.projects_data = ProjectQueryInterface()
        self.openai_session = OpenAI(api_key=gpt_api_key)

    def _get_all_projects_data(self) -> str:
        """
        Retrieves detailed information about all projects in the database, including descriptions, status, rewards,
        links, and requirements.

        :return: A formatted string containing all project data.
        """
        try:
            projects_context = "Available projects data: \n\n"
            all_projects = self.projects_data.get_all_projects()
            for project_name in all_projects:
                project_info = self.projects_data.get_project_info(project_name)
                requirements = self.projects_data.get_requirements_by_project(project_name)
                requirements_context = [f'{r['task']} | {r['difficulty']} | {r['deadline']}' for r in requirements]
                projects_context += f"Project name: '{project_name}':\n" \
                                    f"Short description: {project_info.get('description_short')}\n" \
                                    f"Full description: {project_info.get('description_full')}\n" \
                                    f"Project status: {project_info.get('status')}\n" \
                                    f"Last update: {project_info.get('last_updated')}\n" \
                                    f"Reward amount: {project_info.get('rewards_amount')}. Approximately {project_info.get('rewards_approximate_amount')}\n" \
                                    f"Reward distribution date: {project_info.get('rewards_distribution_date')}\n" \
                                    f"Project links: Website {project_info.get('links_website')}, " \
                                    f"Twitter {project_info.get('links_twitter')}, " \
                                    f"Telegram {project_info.get('links_telegram')}, " \
                                    f"Discord {project_info.get('links_discord')}\n" \
                                    f"Requirements with task title, difficulty, and deadline: {'; '.join(requirements_context)}\n\n"
            return projects_context
        except Exception as e:
            logging.error("Error fetching all project data: %s", str(e))
            return "Unable to fetch project data."

    def _system_prompt(self) -> dict:
        """
        Generates the system prompt containing the assistant's role and context about available projects.

        :return: A dictionary representing the system prompt for the GPT model.
        """
        message = {
            "role": "system",
            "content": (
                "You are an assistant who gives recommendations on crypto projects and airdrops. "
                "You should give relatively concise but informative answers in a conversational format."
                "Depending on the user's question, you have to provide information about a specific project, "
                "compare projects, evaluate the potential reward from the project, and make recommendations "
                "based on the complexity of the requirements. You should only refer to the projects data provided here."
                "You cannot write about other projects except those specified in the system prompt."
                "When generating an answer, you should use only available data.\n" + self._get_all_projects_data()
            )
        }
        return message

    @staticmethod
    def user_prompt(user_input: str) -> dict:
        """
        Formats the user's input into a prompt suitable for the GPT model.

        :param user_input: The user's query or input.
        :return: A dictionary representing the user prompt for the GPT model.
        """
        message = {
            "role": "user",
            "content": f"Give the correct and understandable answer for the user based on the context:\n{user_input}"
        }
        return message

    def _query_gpt(self, prompt: list) -> str:
        """
        Sends a query to OpenAI's GPT-4 model to process text and generate a response.

        :param prompt: A list of messages (system and user prompts) to send to the GPT model.
        :return: The GPT model's response as a string.
        """
        try:
            response = self.openai_session.chat.completions.create(
                model="gpt-4o",
                messages=prompt,
                temperature=0.8,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error("Response generation error: %s", str(e))
            return "Unable to answer."

    def process_query(self, user_input: str) -> str:
        """
        Processes the user's input by generating prompts, querying the GPT model, and returning the result.

        :param user_input: The user's query or request.
        :return: The GPT model's response as a string.
        """
        system_message = self._system_prompt()
        user_message = self.user_prompt(user_input)

        messages_prompt = [system_message, user_message]

        return self._query_gpt(messages_prompt)
