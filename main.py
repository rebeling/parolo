from parolo import Prompt

def main():
    Prompt.set_base_dir("./project-prompts")

    # example from readme

    # Create a simple prompt
    Prompt.create(name="summarize", prompt="Summarize this in three bullet points.")

    # Create another version with different content
    Prompt.create(name="summarize", prompt="Provide a concise summary in bullet points.")

    # List all versions for a prompt
    versions = Prompt.list_versions("summarize")
    print(versions)  # ['v0001.txt', 'v0002.txt']

    Prompt.create("greet", prompt="Hello, world!", metadata={"author": "demo", "type": "greeting"})

    # Get overview of all prompts
    overview = Prompt.overview()
    print(overview)  # {'summarize': 2, 'greet': 1}


if __name__ == "__main__":
    main()
