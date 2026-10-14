# Simple Agent Class: takes a client, model, name and 

class ChkAgent:
    """Minimal agent: a name, a system prompt, a way to produce a response.
    No inheritance tree, no pipeline — just enough to be reusable."""

    def __init__(
            self, 
            name: str, 
            client, 
            model: str, 
            system_prompt: str):            

        print("=============CREATING ChkAgent==================")
        self.name = name
        self.client = client
        self.model = model
        self.system_prompt = system_prompt


    def run(self, input_text: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=self.system_prompt,
            messages=[{"role": "user", "content": input_text}],
        )
        return "".join(b.text for b in response.content if b.type == "text")



def make_subagent(client, model):
    ''' 3 subagents of class Agent of ChkAgent'''
    print("=============CREATING SUBAGENT==================")

    writer = ChkAgent(model= model, client= client,
        name="Writer", system_prompt= "You are a LinkedIn post writer. Write under 200 words.",
    )

    critic  = ChkAgent(model= model, client= client,
        name="critic", system_prompt= "You are a critic. Give exactly 5 numbered suggestions to improve the draft. Do not rewrite it.",
    )

    reviser = ChkAgent(model= model, client= client,
        name="reviser", system_prompt= "You are an editor. Rewrite the draft to address the critique. Output only the revised post.",
    )

    return writer, critic, reviser



# Chain orchestration

def run_chain(writer, critic, reviser, topic: str)-> str:
    print("=============IMPLEMENTING CHAIN==================")
    draft = writer.run(f"Write a LinkedIn post about: {topic}")
    critique = critic.run(f"Draft:\n{draft}\n\nTopic: {topic}")
    revised = reviser.run(f"Draft:\n{draft}\n\nCritique:\n{critique}")
    return {"draft": draft, "critique": critique, "revised": revised}



import anthropic

try:
    client = anthropic.Anthropic(
        base_url="http://localhost:11434",
            api_key="ollama",
            timeout=120.0,
            max_retries=2,
    )
except Exception as e:
    print(f"error creating client {e}")


writer, critic, reviser = make_subagent(client= client, model="gpt-oss:20b-cloud")

output_response = run_chain(
    topic= "what is India",
    writer= writer,
    critic= critic,
    reviser= reviser
)

# -------------------------------------------------------------------------------------------
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule

console = Console()

def print_output(output_response):
    # Display the draft
    console.print(Rule("[bold cyan]DRAFT[/bold cyan]"))
    console.print(
        Panel(
            Markdown(output_response["draft"]),
            title="[bold green]Initial Draft[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
    )

    # Display the critique
    console.print(Rule("[bold cyan]CRITIQUE[/bold cyan]"))
    console.print(
        Panel(
            Markdown(output_response["critique"]),
            title="[bold yellow]Review & Feedback[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        )
    )

    # Display the revised output
    console.print(Rule("[bold cyan]REVISED OUTPUT[/bold cyan]"))
    console.print(
        Panel(
            Markdown(output_response["revised"]),
            title="[bold magenta]Final Version[/bold magenta]",
            border_style="magenta",
            padding=(1, 2)
        )
    )


# Call your function
print_output(output_response)