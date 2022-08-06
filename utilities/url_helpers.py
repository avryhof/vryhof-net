def url_join(*tokens):
    path_parts = []

    for token in tokens:
        token_parts = [x.replace("/", "") for x in token.split("/") if x.strip() not in ["", "/"]]

        for token_part in token_parts:
            path_parts.append(token_part)

    return "/{}".format("/".join(path_parts))
