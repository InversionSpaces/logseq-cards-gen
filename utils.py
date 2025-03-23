def blocks_from_tree(tree):
    blocks = []
    stack = tree
    while stack:
        block = stack.pop()
        blocks.append(block)
        stack.extend(block['children'])

    return blocks