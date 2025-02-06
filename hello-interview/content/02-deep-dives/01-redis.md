# Redis

## Introduction
System designs can involve a dizzying array of different [**technologies**](https://www.hellointerview.com/learn/system-design/in-a-hurry/key-technologies), [**concepts**](https://www.hellointerview.com/learn/system-design/in-a-hurry/core-concepts) and [**patterns**](https://www.hellointerview.com/learn/system-design/in-a-hurry/patterns), but one technology (arguably) stands above the rest in terms of its _versatility:_ Redis. This versatility is important in an interview setting because it allows you to go deep. Instead of learning about dozens of different technologies, you can learn a few useful ones and learn them deeply, which magnifies the chances that you're able to get to the level your interviewer is expecting.

Beyond versatility, Redis is great for its _simplicity_. Redis has a ton of features which resemble data structures you're probably used to from coding (hashes, sets, sorted sets, streams, etc) and which, given a few basics, are easy to reason about how they behave in a distributed system. While many databases involve a lot of magic (optimizers, query planners, etc), with only minor exceptions Redis has remained quite simple and good at what it does best: executing simple operations **fast**.

Ok, Redis is versatile, simple, and useful for system design interviews. Let's learn how it works.
