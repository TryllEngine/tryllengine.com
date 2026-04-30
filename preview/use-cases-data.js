// 84 AI use cases in games, organized by category.
// Filterable by genre and feasibility.
// feasibility: "proven" | "likely" | "experimental" | "speculative"
// available_now: true when achievable with text-only SLM (no TTS/STT/vision/image/audio/RL required).

window.USE_CASES = [
  // --- 1. Dialogue & Conversation ---
  { id: "1.1", cat: "dialogue", title: "Dynamic NPC dialogue", blurb: "Free-form conversation that replaces hand-scripted dialogue trees. NPCs respond to anything the player says — in character, with memory.", feasibility: "proven", models: "SLM 7–8B", genres: ["rpg","survival","adventure","life-sim"], available_now: true },
  { id: "1.2", cat: "dialogue", title: "Voiced NPC conversation", blurb: "TTS speaks every generated line, so dynamic dialogue actually gets voice-acted in real time.", feasibility: "proven", models: "SLM + TTS", genres: ["rpg","visual-novel","adventure","horror","life-sim","survival","stealth","roguelike","strategy"], available_now: false },
  { id: "1.3", cat: "dialogue", title: "Player voice input for dialogue", blurb: "Speech-to-text turns the player's own voice into input for conversations with NPCs.", feasibility: "proven", models: "STT", genres: ["rpg","visual-novel","adventure","horror","life-sim","survival","stealth","social"], available_now: false },
  { id: "1.4", cat: "dialogue", title: "Persuasion as gameplay", blurb: "Convince NPCs with the actual quality of your argument — not a dice roll, not a menu option.", feasibility: "likely", models: "SLM", genres: ["rpg","strategy","stealth","adventure","sports"], available_now: true },
  { id: "1.5", cat: "dialogue", title: "Interrogation & deception detection", blurb: "Extract truth from NPCs who may be lying. The model tracks inconsistency across a conversation.", feasibility: "likely", models: "SLM", genres: ["rpg","adventure","stealth","horror"], available_now: true },
  { id: "1.6", cat: "dialogue", title: "Social engineering / maintain cover", blurb: "Hold a cover identity under questioning. Slip up in what you say and the guard gets suspicious.", feasibility: "likely", models: "SLM + STT", genres: ["stealth","rpg","strategy"], available_now: true },
  { id: "1.7", cat: "dialogue", title: "Natural-language negotiation", blurb: "Trade, diplomacy, and contracts resolved through real conversation instead of sliders.", feasibility: "likely", models: "SLM", genres: ["strategy","rpg","survival","sports"], available_now: true },
  { id: "1.8", cat: "dialogue", title: "Multi-agent NPC conversation", blurb: "NPCs talking to each other — gossiping, arguing, coordinating — while the player eavesdrops.", feasibility: "likely", models: "SLM (batched)", genres: ["rpg","survival","life-sim","strategy"], available_now: true },
  { id: "1.9", cat: "dialogue", title: "Conversational combat resolution", blurb: "Talk your way out of a fight. Encounters can end in dialogue instead of hit points.", feasibility: "experimental", models: "SLM", genres: ["roguelike","rpg","adventure"], available_now: true },
  { id: "1.10", cat: "dialogue", title: "Treaty & contract wording exploits", blurb: "Rules-lawyer your way through negotiated documents; find loopholes in what the NPC agreed to.", feasibility: "experimental", models: "SLM", genres: ["strategy"], available_now: true },
  { id: "1.11", cat: "dialogue", title: "Language-barrier mechanic", blurb: "Progressive translation as a mechanic — you learn the in-world language as you play.", feasibility: "experimental", models: "SLM", genres: ["rpg"], available_now: true },

  // --- 2. Narration & Storytelling ---
  { id: "2.1", cat: "narration", title: "Dynamic room & scene narration", blurb: "Literary-quality descriptions of what the player is seeing, generated fresh each run.", feasibility: "proven", models: "SLM + TTS", genres: ["roguelike","adventure","horror"], available_now: true },
  { id: "2.2", cat: "narration", title: "Procedural quest generation", blurb: "Missions written on the fly that reference the world state, the player's history, and real NPCs.", feasibility: "likely", models: "SLM", genres: ["rpg","survival","roguelike"], available_now: true },
  { id: "2.3", cat: "narration", title: "Dynamic lore generation", blurb: "Books, journals, and inscriptions written at runtime — endlessly readable worldbuilding.", feasibility: "likely", models: "SLM", genres: ["rpg","survival","horror","roguelike"], available_now: true },
  { id: "2.4", cat: "narration", title: "Consequence narrator", blurb: "A narrator voice that comments, with insight, on what the player's choices actually meant.", feasibility: "likely", models: "SLM + TTS", genres: ["rpg","adventure"], available_now: false },
  { id: "2.5", cat: "narration", title: "Unreliable narrator", blurb: "Descriptions can subtly lie, omit, or distort — a controlled fog of storytelling.", feasibility: "experimental", models: "SLM", genres: ["horror","roguelike"], available_now: true },
  { id: "2.6", cat: "narration", title: "Historian / chronicler AI", blurb: "The model writes the history book of your campaign: battles, betrayals, great deeds.", feasibility: "likely", models: "SLM", genres: ["strategy","rpg","survival"], available_now: true },
  { id: "2.7", cat: "narration", title: "Survival diary / journal", blurb: "Your character keeps a journal in their own voice as they struggle to survive.", feasibility: "likely", models: "SLM", genres: ["survival","roguelike","horror"], available_now: true },
  { id: "2.8", cat: "narration", title: "Death retrospective", blurb: "A narrative autopsy of the run you just lost — what went wrong, in prose.", feasibility: "likely", models: "SLM", genres: ["roguelike"], available_now: true },
  { id: "2.9", cat: "narration", title: "Documentary generation", blurb: "A retrospective narration of a play session, like a nature documentary of your city.", feasibility: "experimental", models: "SLM + TTS", genres: ["life-sim","strategy"], available_now: false },
  { id: "2.10", cat: "narration", title: "Run-has-a-story arcs", blurb: "Procedural runs that carry a thematic narrative arc, not just random rooms.", feasibility: "experimental", models: "SLM", genres: ["roguelike"], available_now: true },
  { id: "2.11", cat: "narration", title: "War correspondence", blurb: "Generated letters between rival leaders — declarations, threats, pleas, alliances.", feasibility: "likely", models: "SLM", genres: ["strategy"], available_now: true },
  { id: "2.12", cat: "narration", title: "Dynamic news & media", blurb: "In-world newspapers, TV segments, and radio that report what the player actually did.", feasibility: "likely", models: "SLM", genres: ["life-sim","survival","strategy"], available_now: true },
  { id: "2.13", cat: "narration", title: "Environmental narrator", blurb: "Atmospheric scene descriptions with real literary rhythm — not barked sound cues.", feasibility: "likely", models: "SLM + TTS", genres: ["adventure","horror","rpg"], available_now: false },

  // --- 3. NPC Behavior & Personality ---
  { id: "3.1", cat: "npc", title: "Persistent NPC memory", blurb: "NPCs remember what you said and did — across quests, sessions, and save files.", feasibility: "proven", models: "SLM + Embeddings", genres: ["rpg","visual-novel","adventure","life-sim","survival","stealth","horror","strategy","social"], available_now: true },
  { id: "3.2", cat: "npc", title: "LoRA-driven personality", blurb: "Each NPC is a lightweight adapter on the base model — distinct voices, hot-swappable at runtime.", feasibility: "proven", models: "SLM + LoRAs", genres: ["rpg","visual-novel","strategy"], available_now: true },
  { id: "3.3", cat: "npc", title: "Personality drift over time", blurb: "Characters evolve — they harden, soften, grow bitter, fall in love — from the life they live.", feasibility: "experimental", models: "SLM + adaptive LoRAs", genres: ["visual-novel","life-sim"], available_now: true },
  { id: "3.4", cat: "npc", title: "Autonomous NPC agents", blurb: "NPCs with their own goals, pursued without a designer scripting every step.", feasibility: "likely", models: "SLM + Policy nets", genres: ["life-sim","survival"], available_now: true },
  { id: "3.5", cat: "npc", title: "Gossip & rumor networks", blurb: "Information spreads village-to-village, degrading and mutating on the way.", feasibility: "experimental", models: "SLM", genres: ["rpg"], available_now: true },
  { id: "3.6", cat: "npc", title: "Multi-agent faction politics", blurb: "Alliances, betrayals, and coups that emerge from NPCs reasoning about each other.", feasibility: "experimental", models: "SLM (multi-agent)", genres: ["rpg","strategy","survival"], available_now: true },
  { id: "3.7", cat: "npc", title: "Living schedules with personality", blurb: "NPCs follow daily routines that bend with mood, weather, and what happened yesterday.", feasibility: "likely", models: "SLM + Policy nets", genres: ["stealth","life-sim"], available_now: true },
  { id: "3.8", cat: "npc", title: "Guard suspicion reasoning", blurb: "Guards reason about what they saw — suspicion is a state, not a binary alert flag.", feasibility: "experimental", models: "SLM", genres: ["stealth"], available_now: true },
  { id: "3.9", cat: "npc", title: "Emotional state modeling", blurb: "Mood colors how NPCs behave and speak. Anger, grief, and joy feel different across a scene.", feasibility: "likely", models: "SLM", genres: ["visual-novel","rpg","life-sim"], available_now: true },
  { id: "3.10", cat: "npc", title: "Apprentice NPCs", blurb: "Teach NPCs tasks — farming, fighting, cooking — by example, and watch them get better.", feasibility: "speculative", models: "SLM + behavioral learning", genres: ["survival"], available_now: false },
  { id: "3.11", cat: "npc", title: "Faction emergence", blurb: "Groups self-organize from individuals with compatible goals. No designer wrote them.", feasibility: "speculative", models: "SLM (multi-agent)", genres: ["survival"], available_now: true },
  { id: "3.12", cat: "npc", title: "Adaptive AI personality evolution", blurb: "Opponents evolve their style over the course of a campaign based on games you played.", feasibility: "experimental", models: "SLM + RL", genres: ["strategy"], available_now: false },

  // --- 4. Voice & Audio ---
  { id: "4.1", cat: "voice", title: "Full voice acting for dynamic lines", blurb: "Unlimited dialogue — every generated line is spoken by a real-sounding local voice.", feasibility: "proven", models: "TTS (Kokoro/Piper)", genres: ["rpg","visual-novel","adventure","horror","life-sim","survival","stealth","roguelike","strategy"], available_now: false },
  { id: "4.2", cat: "voice", title: "Voice-commanded gameplay", blurb: "Tell your squad to flank, your car to pit, your army to advance — spoken aloud.", feasibility: "proven", models: "STT + SLM", genres: ["fps","racing","strategy"], available_now: false },
  { id: "4.3", cat: "voice", title: "Dynamic game commentary", blurb: "A color commentator that actually understands what's happening in the match.", feasibility: "likely", models: "SLM + TTS", genres: ["fighting","sports","racing"], available_now: false },
  { id: "4.4", cat: "voice", title: "Voice emotion detection", blurb: "The game hears stress, sincerity, or nervousness in the player's voice and responds.", feasibility: "likely", models: "Audio classifier", genres: ["horror","visual-novel","social"], available_now: false },
  { id: "4.5", cat: "voice", title: "Whisper vs. shout detection", blurb: "Pronunciation and volume affect gameplay — whisper to sneak, shout to attract.", feasibility: "experimental", models: "STT + audio analysis", genres: ["horror","fps"], available_now: false },
  { id: "4.6", cat: "voice", title: "Voice mirroring", blurb: "A character picks up the player's own speech patterns over time.", feasibility: "speculative", models: "STT analysis + TTS", genres: ["visual-novel"], available_now: false },
  { id: "4.7", cat: "voice", title: "Personalized narrator voice", blurb: "Clone any voice on-device so the narrator sounds exactly how the player wants.", feasibility: "likely", models: "XTTS v2", genres: ["rpg","visual-novel","adventure","horror","life-sim","survival","stealth","roguelike"], available_now: false },
  { id: "4.8", cat: "voice", title: "Live translation between players", blurb: "Multiplayer voice chat translated in real time — no localization team required.", feasibility: "experimental", models: "SLM + TTS", genres: ["social"], available_now: false },
  { id: "4.9", cat: "voice", title: "Spell incantation by voice", blurb: "Pronounce the spell to cast it. Mispronounce it and the magic goes wrong.", feasibility: "experimental", models: "STT", genres: ["rpg","adventure"], available_now: false },
  { id: "4.10", cat: "voice", title: "Language learning through gameplay", blurb: "Pick up real-world languages by speaking with NPCs who expect you to.", feasibility: "experimental", models: "STT + SLM", genres: ["rpg","adventure"], available_now: false },

  // --- 5. Adaptive Gameplay ---
  { id: "5.1", cat: "adaptive", title: "Adaptive difficulty (RL)", blurb: "The game reads how the player is doing and tunes itself — quietly, move by move.", feasibility: "proven", models: "Small RL models", genres: ["fighting","rhythm","racing"], available_now: false },
  { id: "5.2", cat: "adaptive", title: "Adaptive opponent AI", blurb: "The AI learns your patterns and counters them within a single match.", feasibility: "proven", models: "RL policy networks", genres: ["fighting","strategy"], available_now: false },
  { id: "5.3", cat: "adaptive", title: "Biometric fear adaptation", blurb: "Webcam and mic feed emotion cues back into the game to amplify horror.", feasibility: "experimental", models: "MediaPipe + classifiers", genres: ["horror"], available_now: false },
  { id: "5.4", cat: "adaptive", title: "Psychological profiling", blurb: "The horror game learns what scares you personally — and leans on it.", feasibility: "experimental", models: "Behavioral models", genres: ["horror"], available_now: false },
  { id: "5.5", cat: "adaptive", title: "Dynamic coaching", blurb: "Personal tactical advice based on what the game actually saw you do.", feasibility: "likely", models: "SLM + game state", genres: ["fps","racing","fighting","sports"], available_now: true },
  { id: "5.6", cat: "adaptive", title: "Dynamic tutorial generation", blurb: "Just-in-time help, phrased for exactly the moment the player is stuck.", feasibility: "likely", models: "SLM", genres: ["rpg","visual-novel","fps","fighting","survival","horror","adventure","life-sim","racing","stealth","roguelike","sports","rhythm","social","strategy"], available_now: true },
  { id: "5.7", cat: "adaptive", title: "Procedural level design that learns you", blurb: "Generators that tune their output to the player's taste over many runs.", feasibility: "experimental", models: "RL", genres: ["roguelike"], available_now: false },
  { id: "5.8", cat: "adaptive", title: "Dynamic economy balancing", blurb: "Market prices, loot tables, and rewards adjusted live to keep the game honest.", feasibility: "experimental", models: "RL", genres: ["survival","life-sim"], available_now: false },
  { id: "5.9", cat: "adaptive", title: "Player-behavior matchmaking", blurb: "Embedding-based clustering so the matchmaker finds opponents who fit your style.", feasibility: "likely", models: "Embedding models", genres: ["fps","fighting","sports","racing","social","strategy"], available_now: true },

  // --- 6. Visual & Image ---
  { id: "6.1", cat: "visual", title: "Dynamic character portraits", blurb: "Portraits that redraw themselves as the character's mood, wounds, or outfit change.", feasibility: "experimental", models: "LCM/SDXL Turbo + LoRA", genres: ["visual-novel"], available_now: false },
  { id: "6.2", cat: "visual", title: "Player-described visualization", blurb: "Describe your sword, your armor, your familiar — the game renders it.", feasibility: "likely", models: "SDXL Turbo / LCM", genres: ["rpg","survival"], available_now: false },
  { id: "6.3", cat: "visual", title: "Procedural environment textures", blurb: "Surfaces generated on demand so no two caves or alleys ever look the same.", feasibility: "experimental", models: "LCM", genres: ["roguelike","survival"], available_now: false },
  { id: "6.4", cat: "visual", title: "Evidence & document generation", blurb: "Newspapers, photos, and letters for mystery and detective gameplay — generated in-world.", feasibility: "likely", models: "SDXL Turbo", genres: ["adventure","strategy"], available_now: false },
  { id: "6.5", cat: "visual", title: "Art as gameplay", blurb: "Draw-and-judge mechanics powered by image generation — the game plays back.", feasibility: "experimental", models: "Image gen", genres: ["social"], available_now: false },
  { id: "6.6", cat: "visual", title: "Webcam facial emotion", blurb: "The character in the visual novel sees you react — and reacts back.", feasibility: "likely", models: "MediaPipe + CNN", genres: ["horror","visual-novel","social"], available_now: false },
  { id: "6.7", cat: "visual", title: "Gesture-based input", blurb: "Cast spells with your hands, command units with gestures — hand tracking to gameplay.", feasibility: "experimental", models: "MediaPipe", genres: ["rpg","strategy"], available_now: false },
  { id: "6.8", cat: "visual", title: "Mixed-reality object recognition", blurb: "Hold a real object to the camera and the game reads it into play.", feasibility: "speculative", models: "Small VLM (Florence-2)", genres: ["adventure","social"], available_now: false },
  { id: "6.9", cat: "visual", title: "Real-time expression → avatar", blurb: "Your face drives your avatar's face, live, without motion-capture gear.", feasibility: "experimental", models: "MediaPipe", genres: ["rpg","visual-novel","social","life-sim"], available_now: false },
  { id: "6.10", cat: "visual", title: "Screen reading for coaching", blurb: "A vision model watches the screen with you and coaches as you play.", feasibility: "experimental", models: "Small VLM", genres: ["fps","fighting","sports","racing","strategy","rpg"], available_now: false },

  // --- 7. Music & Sound ---
  { id: "7.1", cat: "music", title: "Procedural music from prompts", blurb: "Describe the mood, get the track — generated locally, at runtime.", feasibility: "proven", models: "MusicGen Small", genres: ["rhythm"], available_now: false },
  { id: "7.2", cat: "music", title: "Adaptive soundtrack", blurb: "Score responds to game state — tension, exploration, victory — without crossfades.", feasibility: "likely", models: "MusicGen + game state", genres: ["rpg","horror","fps","adventure","survival","strategy","roguelike","racing","fighting","sports","rhythm","life-sim"], available_now: false },
  { id: "7.3", cat: "music", title: "Character theme generation", blurb: "Every companion and villain gets their own theme, written for them.", feasibility: "experimental", models: "MusicGen", genres: ["rpg","visual-novel"], available_now: false },
  { id: "7.4", cat: "music", title: "Player-composed music as play", blurb: "Bard classes and rhythm games where what you play is the mechanic.", feasibility: "experimental", models: "Audio analysis + MusicGen", genres: ["rpg","rhythm"], available_now: false },
  { id: "7.5", cat: "music", title: "Generative sound effects", blurb: "SFX written at runtime for situations the sound designer couldn't pre-record.", feasibility: "experimental", models: "Audio models", genres: ["rpg","horror","fps","adventure","survival","strategy","roguelike","racing","fighting","sports","life-sim","stealth"], available_now: false },
  { id: "7.6", cat: "music", title: "Collaborative jam session", blurb: "An AI band member that improvises alongside you, in time, in key.", feasibility: "speculative", models: "Real-time audio model", genres: ["rhythm"], available_now: false },
  { id: "7.7", cat: "music", title: "Dynamic crowd audio", blurb: "Spectator sound that actually reacts to what's happening in the arena.", feasibility: "experimental", models: "Audio gen / SFX models", genres: ["fighting","sports"], available_now: false },
  { id: "7.8", cat: "music", title: "Emotion-reactive music", blurb: "A biofeedback loop — the score reads you and shifts to hold the mood.", feasibility: "speculative", models: "Emotion detection + MusicGen", genres: ["horror","rpg","visual-novel"], available_now: false },

  // --- 8. Meta / Cross-genre ---
  { id: "8.1", cat: "meta", title: "In-game knowledge assistant", blurb: "A search engine for the world — the player asks, the model answers in character.", feasibility: "likely", models: "SLM + game knowledge base", genres: ["rpg","visual-novel","fps","fighting","survival","horror","adventure","life-sim","racing","stealth","roguelike","sports","rhythm","social","strategy"], available_now: true },
  { id: "8.2", cat: "meta", title: "Natural-language accessibility", blurb: "Speak (or type) what you want to do. The SLM maps it to game actions.", feasibility: "likely", models: "SLM + STT", genres: ["rpg","visual-novel","fps","fighting","survival","horror","adventure","life-sim","racing","stealth","roguelike","sports","rhythm","social","strategy"], available_now: false },
  { id: "8.3", cat: "meta", title: "Full game voicing (accessibility)", blurb: "All on-screen text read aloud — menus, subtitles, codex entries.", feasibility: "proven", models: "TTS", genres: ["rpg","visual-novel","fps","fighting","survival","horror","adventure","life-sim","racing","stealth","roguelike","sports","rhythm","social","strategy"], available_now: false },
  { id: "8.4", cat: "meta", title: "Player wellness", blurb: "Posture, blink-rate, fatigue cues — the game suggests a break when you need one.", feasibility: "likely", models: "MediaPipe", genres: ["rpg","visual-novel","fps","fighting","survival","horror","adventure","life-sim","racing","stealth","roguelike","sports","rhythm","social","strategy"], available_now: false },
  { id: "8.5", cat: "meta", title: "Semantic crafting", blurb: "Combine items by meaning — 'water' + 'fire' → 'steam' — via embeddings, not a table.", feasibility: "experimental", models: "Embedding model + SLM", genres: ["rpg","survival"], available_now: true },
  { id: "8.6", cat: "meta", title: "Semantic search in the world", blurb: "'Where did I leave the silver key?' — the game actually knows.", feasibility: "likely", models: "Embedding model", genres: ["rpg","adventure","survival"], available_now: true },
  { id: "8.7", cat: "meta", title: "Fourth-wall-breaking AI", blurb: "An antagonist that knows things about the real world. Use sparingly.", feasibility: "experimental", models: "SLM + system context", genres: ["horror","roguelike"], available_now: true },
  { id: "8.8", cat: "meta", title: "AI fill-in players", blurb: "An SLM-powered teammate that stands in when the fifth player doesn't show.", feasibility: "likely", models: "SLM + behavioral model", genres: ["social","fps"], available_now: true },
  { id: "8.9", cat: "meta", title: "AI moderation & refereeing", blurb: "A referee for party games, a moderator for chat — on-device, private.", feasibility: "likely", models: "SLM", genres: ["social"], available_now: true },
  { id: "8.10", cat: "meta", title: "Collaborative puzzle design", blurb: "Players and the model co-author puzzles, then trade them with friends.", feasibility: "experimental", models: "SLM", genres: ["adventure","roguelike"], available_now: true }
];

window.CATEGORIES = [
  { id: "dialogue", name: "Dialogue & Conversation", short: "Dialogue" },
  { id: "narration", name: "Narration & Storytelling", short: "Narration" },
  { id: "npc", name: "NPC Behavior & Personality", short: "NPC Behavior" },
  { id: "voice", name: "Voice & Audio", short: "Voice" },
  { id: "adaptive", name: "Adaptive Gameplay", short: "Adaptive" },
  { id: "visual", name: "Visual & Image", short: "Visual" },
  { id: "music", name: "Music & Sound", short: "Music" },
  { id: "meta", name: "Meta / Cross-Genre", short: "Meta" }
];

window.GENRES = [
  { id: "rpg", name: "RPG", blurb: "Western, JRPG, Action RPG. Dialogue, quests, companions." },
  { id: "visual-novel", name: "Visual Novel", blurb: "Dating sims and kinetic novels. The whole game is conversation." },
  { id: "strategy", name: "Strategy", blurb: "RTS, Turn-based, 4X. Diplomacy, advisors, opponent reasoning." },
  { id: "fps", name: "FPS / TPS", blurb: "Shooters. Squad voice commands, briefings, banter." },
  { id: "fighting", name: "Fighting", blurb: "1v1 combat. Adaptive opponents, commentary, coaching." },
  { id: "survival", name: "Survival / Sandbox", blurb: "Open world. Emergent NPC communities, procedural narrative." },
  { id: "horror", name: "Horror", blurb: "Psychological profiling, unreliable narration, adaptive scares." },
  { id: "adventure", name: "Adventure / Puzzle", blurb: "Narrative puzzles. Conversational NPCs, hint systems." },
  { id: "life-sim", name: "Life Sim / Management", blurb: "Sims-like, city builders. Agents with memory and mood." },
  { id: "racing", name: "Racing", blurb: "High-speed driving. Co-drivers, commentary, pit strategy." },
  { id: "stealth", name: "Stealth / Immersive Sim", blurb: "Guards that reason, cover stories, social infiltration." },
  { id: "roguelike", name: "Roguelike", blurb: "Procedural runs with a story, death retrospectives, dungeon masters." },
  { id: "sports", name: "Sports", blurb: "AI coaches, scouting reports, natural-language team management." },
  { id: "rhythm", name: "Rhythm / Music", blurb: "Generative soundtracks, AI DJs, procedural tracks." },
  { id: "social", name: "Social / Party", blurb: "Moderators, fill-in players, live translation." }
];

window.FEASIBILITY = {
  proven: { label: "Proven", blurb: "Shipping today." },
  likely: { label: "Likely", blurb: "Technically straightforward." },
  experimental: { label: "Experimental", blurb: "Needs R&D." },
  speculative: { label: "Speculative", blurb: "Unproven concept." }
};
