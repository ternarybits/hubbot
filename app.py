import os
from slack_bolt import App
import openai

# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Initializes OpenAI
openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")

######################################################################################
# Event handlers go down here


@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        # views.publish is the method that your app uses to push a view to the Home tab
        client.views_publish(
            # the user that opened your app's app home
            user_id=event["user"],
            # the view object that appears in the app home
            view={
                "type": "home",
                "callback_id": "home_view",

                # body of the view
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Welcome to your _App's Home_* :tada:"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Click me!"
                                }
                            }
                        ]
                    }
                ]
            }
        )

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


@app.event("app_mention")
def reply_to_mention(client, event, logger):
    try:
        print("Got an app_mention event!")
        channel_id = event['channel']
        user_id = event["user"]
        text = f"Welcome, <@{user_id}>!"
        client.chat_postMessage(text=text, channel=channel_id)
    except Exception as e:
        logger.error(f"Error handling app_mention event: {e}")


@app.command("/imagine")
def repeat_text(ack, respond, command):
    ack()
    prompt = command['text']
    user_id = command['user_id']
    respond(f"Working on generating an image of \"{prompt}\"...")
    image_url = generate_image(prompt)
    respond(text=f"Generated image: {image_url} for user ____",
            response_type="in_channel",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"<@{user_id}> requested image for \"{prompt}\""
                    }
                },
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": prompt,
                    },
                    "block_id": "image4",
                    "image_url": image_url,
                    "alt_text": prompt
                }
            ])


def generate_image(prompt: str) -> str:
    # Ask OpenAI to create an image
    # Test image that can be subbed in to reduce API usage during development
    # return "https://oaidalleapiprodscus.blob.core.windows.net/private/org-sD89XSS7Xb38H7k2tDo66a6f/user-CabKEhEV0rkNnPTEX5n59qti/img-fKiNLCPZ2WQMw5YsZwQaz7KI.png?st=2022-11-04T18%3A16%3A58Z&se=2022-11-04T20%3A16%3A58Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2022-11-04T01%3A02%3A36Z&ske=2022-11-05T01%3A02%3A36Z&sks=b&skv=2021-08-06&sig=E8/twtAH0Fyhf01x6WAdYVXQaACx7JyD/EXlEqPRJM8%3D"
    response = openai.Image.create(
      prompt=prompt,
      n=1,
      size="512x512"
    )
    return response['data'][0]['url']


# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
