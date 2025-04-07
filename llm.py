import requests

def construct_prompt(docs, query):
    prompt = "Context: \n"
    for doc in docs:
        prompt += doc[0].page_content + "\n-------------------------------------------------------\n"
    prompt += "Query: " + query
    return prompt

def llm_call(config, sys_prompt, prompt):
    headers = {
          "Authorization": f"Bearer {config["llm"]["api_key"]}",
          "Content-Type": "application/json"
    }
    data = {
        "model": config["llm"]["model_name"],
        "messages": [
          {"role": "system", "content": sys_prompt},
          {"role": "user", "content": prompt}
        ],
        "temperature": config["llm"]["params"]["temperature"],
        "stream": False
    }
    response = requests.post(url=config["llm"]["endpoint"], headers=headers, json=data)
    return response