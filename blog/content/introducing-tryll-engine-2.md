We've been working hard over the past few months, and today we're excited to share the biggest update to Tryll Engine since launch. Version 2.0 is a ground-up rethink of how local AI should work in games.

## What's New

### 3x Faster Inference

Our new inference pipeline squeezes significantly more performance out of consumer GPUs. On an RTX 4070, response times for a 7B model dropped from ~120ms to under 40ms — well within the range needed for real-time gameplay.

The key improvements:

- **Speculative decoding** with a small draft model that predicts likely token sequences
- **KV-cache optimizations** that reduce memory bandwidth bottlenecks
- **Better batching** of concurrent NPC requests when multiple characters need to think at once

### Latest Model Support

Tryll 2.0 ships with support for the newest open-source models out of the box:

| Model | Parameters | VRAM Required | Best For |
|-------|-----------|---------------|----------|
| Qwen 3 | 4B | 3 GB | Low-end systems, simple dialogue |
| Llama 4 Scout | 8B | 6 GB | Balanced performance and quality |
| Mistral Medium | 14B | 10 GB | Complex reasoning, multi-step plans |

The LLM Manager automatically selects the best model for each player's hardware on first launch. No configuration needed.

### Redesigned Developer API

The old API required too much boilerplate. We've simplified everything down to a few core concepts:

```csharp
// Old way - verbose
var config = new TryllConfig();
config.SetModelPath("models/");
config.SetMaxTokens(256);
config.SetTemperature(0.7f);
var engine = new TryllEngine(config);
engine.Initialize();
var response = engine.GenerateResponse(context, prompt);

// New way - clean
var tryll = Tryll.Init();
var response = await tryll.Ask(npc, "What should I say to the player?");
```

The new API handles model selection, context management, and memory automatically. You focus on game design — we handle the AI plumbing.

## Performance Benchmarks

We tested across a range of common gaming GPUs:

- **RTX 3060 (12GB)** — 8B model at ~65ms per response
- **RTX 4070 (12GB)** — 8B model at ~38ms per response
- **RTX 4070 Ti Super (16GB)** — 14B model at ~52ms per response
- **RTX 4090 (24GB)** — 14B model at ~28ms per response

All tests used realistic game scenarios with 2K token context windows. Frame rate impact was less than 3% in all cases.

## Migration Guide

Upgrading from 1.x? The migration is straightforward:

1. Update the Tryll SDK package to 2.0
2. Replace `TryllEngine` initialization with `Tryll.Init()`
3. Swap `GenerateResponse()` calls with `Ask()`
4. Remove manual model configuration (now handled automatically)

We've kept backward compatibility for the core `GenerateResponse` method, so nothing will break immediately. But we recommend migrating to the new API for better performance and simpler code.

## What's Next

We're already working on the next set of features:

- **Voice synthesis** — local text-to-speech for NPC dialogue
- **Emotion detection** — understanding player tone from text input
- **Multi-NPC coordination** — NPCs that can discuss and plan together

Stay tuned, and as always, come chat with us on [Discord](https://discord.gg/XCBBGUMzUM) if you have questions.
