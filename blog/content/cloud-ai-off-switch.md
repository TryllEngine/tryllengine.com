On Friday, Claude Fable 5 was shut down for everyone, worldwide, on a government order. Four days later, it's still unavailable with no restoration date. Imagine you'd built a game based on this tech. What will break if the AI model behind it gets switched off like that?

![Glory to Fable 5](/assets/blog/cloud-ai-off-switch-inline-1.jpg)

We at Tryll Engine are interested in this kind of situation developers might encounter. And here we will be sharing topics at the crossroads of gamedev and AI to discuss them with the community.

For anything cosmetic (a bit of flavor text, an internal art production workflow), the answer is "not much." For anything load-bearing (a core NPC system, the feature your trailer is built around), a cloud model is a live third-party dependency. And with AI driving unprecedented compute demand, it can change price, change policy, rate-limit you, or in this case get switched off by someone who is neither you nor your vendor.

Your players never see the directive. They see a broken feature.

Two costs hide in that. The obvious one is control: someone else holds the off switch. The quieter one is the bill. Serving cloud AI to 10,000 concurrent players runs roughly $1.8M a month, a line that scales against you with every hit you ship.

On-device inference answers both. The model runs on the player's own GPU, so there's no monthly serving bill and no off switch anyone else can reach. It carries real challenges and tradeoffs, for instance, hardware coverage. We at Tryll value transparency, and we'll be talking about the problems here, out in the open.

Stay tuned and drop a line in the comments: what's the hardest part when you think about integrating AI into your game?
