from dpoll import *

if __name__ =="__main__":
    question = input("Question: ")
    options = input("Options: ").split("; ")
    nauth = int(input("Number of authorities: "))

    if len(options) == 2:
        poll = Shamir2Poll(
            nauth = nauth,
            question = question,
            options = options
        )
    else:
        poll = ShamirNPoll(
            nauth = nauth,
            question = question,
            options = options
        )

    command = input("> ")

    while command != "finish":
        if command == "vote":
            ballot = input("Option? ")
            if ballot not in options:
                print("Invalid option")
                continue
            amount = int(input("How many votes? "))
            for i in range(amount):
                poll.vote(ballot)
        elif command == "results":
            poll.results()
        else:
            print("Invalid command")
        command = input("> ")

    print("Poll finished!\n")

    poll.results()
