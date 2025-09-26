from parolo import set_base_dir, prompts, Prompt # new + old


def main():
    path = "./project-prompts"

    Prompt.set_base_dir(path) # old
    set_base_dir(path) # new

    # example from readme

    # New, namespaced API
    prompts.save("greeting", "Hello {{name}}!")
    print(prompts.render("greeting", name="Matthias"))

    # Old class API (back-compat, str.format)
    Prompt.create("legacy", "Hi {name}")
    print(Prompt.format_prompt("legacy", name="Matthias"))

    # List all versions for a prompt
    versions = Prompt.list_versions("legacy")
    print(versions)  # ['v0001.txt', 'v0002.txt']

    # Get overview of all prompts
    overview = Prompt.overview()
    print(overview)  # {'greeting': 1, 'summarize': 1}


if __name__ == "__main__":
    main()
