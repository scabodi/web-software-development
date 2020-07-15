def keyword_usage(input1, input2):
    to_check = input1.split()
    to_return = ()
    for i in range(len(input2)):
        if input2[i] in to_check:
            to_return += (True,)
        else:
            to_return += (False,)

    return to_return
