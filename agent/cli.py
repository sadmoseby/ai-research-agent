import argparse

from agent.graph import build_graph


def main():
    p = argparse.ArgumentParser()
    p.add_argument("propose", nargs="?")
    p.add_argument("--idea", required=True)
    p.add_argument("--alpha-only", action="store_true")
    p.add_argument("--slug", default=None)
    args = p.parse_args()

    app = build_graph()
    state = app.invoke(
        {
            "idea": args.idea,
            "alpha_only": bool(args.alpha_only),
            "slug": args.slug or args.idea.lower().replace(" ", "_")[:64],
        },
        config={"configurable": {"thread_id": args.slug or "default"}},
    )

    print("Done. See proposals/ for output.")


if __name__ == "__main__":
    main()
