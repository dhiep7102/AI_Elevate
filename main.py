import os
import argparse
import sys
from collector import collect_all
from analyzer import summarize_articles

def main():
    print("📰 Vietnam News InsightFlow AI")
    print("Type a topic to summarize news (e.g., economy, politics, tech).")
    print("Type 'exit' or 'quit' to stop.\n")

    # Collect news once to save API calls
    articles = collect_all()
    print("✅ News data collected. Ready for analysis.\n")

    while True:
        topic = input("Enter topic: ").strip()
        if topic.lower() in ["exit", "quit"]:
            print("👋 Exiting InsightFlow AI. Goodbye!")
            break

        if not topic:
            print("⚠️ Please enter a topic or type 'exit' to quit.\n")
            continue

    # articles = collect_all()
        summary = summarize_articles(articles, topic)
        print("\n✅ Summary:\n", summary)

if __name__ == '__main__':
    main()