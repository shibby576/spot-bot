# SpotBot: Autonomous Spotify agent and DJ
SpotBot is your Spotify sidekick who can control your music player, find similar songs, and add songs to your queue. 

The purpose of this project was to learn how to build an agent with Langchain that could display its reasoning capabilities by using several tools in sequence and by taking an action that could be seen immediately. Fortunately, Spotify's developer friendly API has many of the components necessary to enable these types of multi-step actions. 

For example, when prompting SpotBot with *"Find a similar song to whats playing and add it to queue"*, its able to reason through the following steps:
  - First I need to figure out what song is currently playing --> "Check current song" tool, returns a song uri
  - Then I need call Spotify to get a similar song --> "Find similar song" tool, takes song uri as input and returns a song uri
  - Then I need to add that new uri to the queue --> "Add song to queue" tool, takes song uri as input

Two interesting things about this type of flow are one, that the agent understands which tools to use and in which order simply by the descriptions of the tools and prompt, and two, that when the agent encounters an issue, it often is able to reason its way to a useful outcome. Both of these capabilities make programming this sort of application much faster than traditional methods, though there are still many downsides (latency, inconsistency, etc).

[Video demo](https://www.linkedin.com/posts/jonathanehirko_llm-ai-startups-activity-7082731257796718593-pugH/?utm_source=share&utm_medium=member_desktop) | [Live site](https://www.spot-bot.xyz/) 

