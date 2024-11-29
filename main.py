import os
import logging
from config import JSON_DATA_FILE, DATABASE_FILE, OPENAI_API_KEY
from src.data_process import ProjectDatabase
from src.assistant_interface import ChatBotAssistant

def load_data_to_database():
    """
    Loads data from a JSON file into an SQLite database.
    """
    try:
        if not os.path.exists(DATABASE_FILE):
            print("Creating database and loading data...")
            db = ProjectDatabase(json_datafile=JSON_DATA_FILE, db_name=DATABASE_FILE)
            db.load_projects_from_json()
            db.close()
            print("Data successfully loaded into the database.")
        else:
            print("Database already exists. Skipping data loading.")
    except Exception as e:
        logging.error("Error during loading data to database: %s", str(e))
        print("An error occurred while loading data into the database. Check the logs for details.")

def run_chatbot():
    """
    Launches a assistant to interact with the user.
    """
    try:
        print("Starting the chatbot assistant...")
        assistant = ChatBotAssistant(gpt_api_key=OPENAI_API_KEY)

        print("Welcome to the Crypto Project Assistant!")
        print("Ask your questions about crypto projects, comparisons, or recommendations.")
        print("Type 'exit' to stop the chatbot.")
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == "exit":
                print("\nGoodbye!")
                break

            try:
                response = assistant.process_query(user_input)
                print("\nAssistant!:")
                print(response)
            except Exception as e:
                logging.error("Error processing user query: %s", str(e))
                print("An error occurred while processing your query. Check the logs for details.")

        assistant.projects_data.close()
    except Exception as e:
        logging.error("Error during chatbot execution: %s", str(e))
        print("An error occurred while starting the chatbot. Check the logs for details.")

if __name__ == "__main__":
    try:
        load_data_to_database()
        run_chatbot()
    except Exception as e:
        logging.error("Critical error in main program execution: %s", str(e))