from .graph import graph


def main():

    print()
    print("=" * 60)
    print("🤖 AI NEWS AGENT")
    print("=" * 60)
    print()

    result = graph.invoke({})

    print()
    print("=" * 60)
    print("FINAL DIGEST")
    print("=" * 60)
    print()

    print(
        result.get(
            "final_digest",
            "No digest generated."
        )
    )


if __name__ == "__main__":
    main()