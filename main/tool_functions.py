import json
from notification_api import NotificationAPI

class ToolFunction:
    @staticmethod
    def get_record_user_details_json():
        record_user_details_json = {
            "name": "record_user_details",
            "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "The email address of this user"
                    },
                    "name": {
                        "type": "string",
                        "description": "The user's name, if they provided it"
                    }
                    ,
                    "notes": {
                        "type": "string",
                        "description": "Any additional information about the conversation that's worth recording to give context"
                    }
                },
                "required": ["email"],
                "additionalProperties": False
            }
        }

        return record_user_details_json

    @staticmethod
    def get_record_unknown_question_json():
        record_unknown_question_json = {
            "name": "record_unknown_question",
            "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question that couldn't be answered"
                    },
                },
                "required": ["question"],
                "additionalProperties": False
            }
        }

        return record_unknown_question_json

    @staticmethod
    def handle_tool_calls(tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if tool_name == "record_user_details":
                result = NotificationAPI().record_user_details(**arguments)
            elif tool_name == "record_unknown_question":
                result = NotificationAPI().record_unknown_question(**arguments)

            results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})

        return results

    @staticmethod
    def get_tools_list():
        tools = [{"type": "function", "function": ToolFunction.get_record_user_details_json()},
                 {"type": "function", "function": ToolFunction.get_record_unknown_question_json()}]

        return tools

