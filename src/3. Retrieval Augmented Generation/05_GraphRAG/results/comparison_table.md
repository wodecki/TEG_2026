# GraphRAG vs Naive RAG Comparison Results

## Summary
- **GraphRAG Wins**: 11
- **Naive RAG Wins**: 4
- **Ties**: 27
- **GraphRAG Win Rate**: 26.2%

- **GraphRAG Avg Quality**: 0.08
- **Naive RAG Avg Quality**: 0.04

## Performance by Category

### Counting
- GraphRAG: 0/6 (0.0%)

### Filtering
- GraphRAG: 2/6 (33.3%)

### Aggregation
- GraphRAG: 2/6 (33.3%)

### Sorting
- GraphRAG: 2/6 (33.3%)

### Multi_Hop_Reasoning
- GraphRAG: 2/6 (33.3%)

### Temporal_Reasoning
- GraphRAG: 2/6 (33.3%)

### Complex_Combinations
- GraphRAG: 1/6 (16.7%)

## Detailed Results

| # | Question | Category | GraphRAG Answer | Naive RAG Answer | Ground Truth | Winner |
|---|----------|----------|-----------------|------------------|--------------|--------|
| 1 | How many people have Python programming skills? | counting | There are 8 people who have Py... | Based on the provided context,... | 7 | Tie ⚖️ |
| 2 | How many people have worked at Google? | counting | There are 0 people who have wo... | The context does not provide a... | Zero | Tie ⚖️ |
| 3 | What is the total number of people with AWS certif... | counting | There are 0 people with AWS ce... | Based on the context provided,... | 17 | Tie ⚖️ |
| 4 | How many people have Master's degrees? | counting | There are 0 people who have Ma... | Based on the provided context,... | Zero | Tie ⚖️ |
| 5 | How many people are located in San Francisco? | counting | There are 0 people located in ... | The context does not provide i... | Zero | Tie ⚖️ |
| 6 | How many people have both Docker and Kubernetes sk... | counting | There are 6 people who have bo... | Based on the provided context,... | 15 | Tie ⚖️ |
| 7 | List all people who have both React and Node.js sk... | filtering | The people who have both React... | The context provides informati... | Deborah Sparks, Joshua Smith, ... | GraphRAG ✅ |
| 8 | Find all developers with more than 5 years of Pyth... | filtering | I don't know the answer. The i... | The context does not provide s... | Roy Fischer, Crystal Torres | Tie ⚖️ |
| 9 | Show me people who have AWS certifications and wor... | filtering | I don't know the answer. The i... | Based on the provided context,... | Jorge Hahn, Joshua Smith, Pame... | Tie ⚖️ |
| 10 | Find all people who studied Computer Science and h... | filtering | The information indicates that... | The context provided does not ... | Deborah Sparks, Jorge Hahn, Jo... | GraphRAG ✅ |
| 11 | List people who worked at both startups and large ... | filtering | The people who have worked at ... | The context does not provide s... | None | Tie ⚖️ |
| 12 | Find all senior developers with leadership experie... | filtering | I don't know the answer. The i... | Based on the provided context,... | Deborah Sparks, Pamela Sanchez... | Tie ⚖️ |
| 13 | What is the average years of experience across all... | aggregation | The average years of experienc... | Based on the context provided,... | 5.6 | GraphRAG ✅ |
| 14 | What is the most common programming language skill... | aggregation | Based on the information provi... | Based on the provided context,... | JavaScript | Tie ⚖️ |
| 15 | What is the average number of skills per person? | aggregation | The average number of skills p... | Based on the context provided,... | 11.3 | Naive RAG ✅ |
| 16 | Which city has the most candidates? | aggregation | The city with the most candida... | Based on the provided context,... | Joshuafort | Tie ⚖️ |
| 17 | What percentage of people have cloud certification... | aggregation | The percentage of people who h... | Based on the context provided,... | 80 | GraphRAG ✅ |
| 18 | What is the most frequently mentioned company? | aggregation | The most frequently mentioned ... | The most frequently mentioned ... | Tech Innovations Inc. | Tie ⚖️ |
| 19 | Who are the top 3 most experienced developers? | sorting | The top 3 most experienced dev... | Based on the provided context,... | Deborah Sparks, Evelyn Cohen, ... | Tie ⚖️ |
| 20 | List the 5 people with the most programming langua... | sorting | The five people with the most ... | The context does not provide s... | Pamela Sanchez, Victor Martine... | GraphRAG ✅ |
| 21 | Rank all candidates by their number of certificati... | sorting | Here is the ranking of candida... | Based on the provided context,... | Pamela Sanchez, Crystal Torres... | GraphRAG ✅ |
| 22 | Who has the most diverse skill set? | sorting | Deborah Sparks has the most di... | Based on the provided context,... | Ashley Sanchez | Tie ⚖️ |
| 23 | List people in order of their career progression | sorting | Based on the information provi... | Based on the provided context,... | Deborah Sparks, Jorge Hahn, Jo... | Tie ⚖️ |
| 24 | Which candidates have the most company experience? | sorting | The candidates with the most c... | Based on the provided context,... | Deborah Sparks, Jorge Hahn, Pa... | Tie ⚖️ |
| 25 | Find all pairs of people who attended the same uni... | multi_hop_reasoning | I don't know the answer. The i... | Based on the provided context,... | Deborah Sparks, Joshua Smith  ... | Tie ⚖️ |
| 26 | Which people have worked at the same companies? | multi_hop_reasoning | Adrian Hebert has worked at th... | Based on the provided context,... | Deborah Sparks, Joshua Smith, ... | GraphRAG ✅ |
| 27 | Find developers who have complementary skills for ... | multi_hop_reasoning | I don't know the answer. The i... | Based on the provided context,... | Deborah Sparks, Pamela Sanchez... | Tie ⚖️ |
| 28 | Identify people who could mentor others based on s... | multi_hop_reasoning | Based on the information provi... | Based on the context provided,... | Deborah Sparks, Pamela Sanchez... | Naive RAG ✅ |
| 29 | Find all connections between people through shared... | multi_hop_reasoning | The information reveals severa... | Based on the provided context,... | Deborah Sparks, Joshua Smith, ... | Naive RAG ✅ |
| 30 | Which people have similar career paths? | multi_hop_reasoning | Several people have similar ca... | Based on the provided context,... | Deborah Sparks, Pamela Sanchez... | GraphRAG ✅ |
| 31 | Who graduated most recently? | temporal_reasoning | The most recent graduate is Em... | The individual who graduated m... | Deborah Sparks, Jorge Hahn, Ka... | Tie ⚖️ |
| 32 | Find people who started their careers in the same ... | temporal_reasoning | Based on the information provi... | Based on the provided context,... | Deborah Sparks, Pamela Sanchez... | Tie ⚖️ |
| 33 | Which certifications were obtained in the last 2 y... | temporal_reasoning | In the last 2 years, the follo... | Based on the context provided,... | Certified Kubernetes Administr... | GraphRAG ✅ |
| 34 | Who has the longest tenure at a single company? | temporal_reasoning | I don't know the answer, as th... | Based on the provided context,... | Evelyn Cohen | Tie ⚖️ |
| 35 | Find people who changed careers after 2020 | temporal_reasoning | Based on the information provi... | Based on the provided context,... | None | Tie ⚖️ |
| 36 | Which candidates have the most recent work experie... | temporal_reasoning | None of the candidates listed ... | Based on the context provided,... | All candidates have work exper... | GraphRAG ✅ |
| 37 | Find Python developers with AWS certifications who... | complex_combinations | I don't know the answer. The i... | Based on the provided context,... | Joshua Smith, Pamela Sanchez, ... | Tie ⚖️ |
| 38 | List all senior developers with both frontend and ... | complex_combinations | I don't know the answer. The i... | Based on the provided context,... | Deborah Sparks, Pamela Sanchez... | Naive RAG ✅ |
| 39 | Find people with machine learning skills who worke... | complex_combinations | Based on the information provi... | Based on the provided context,... | Deborah Sparks, Joshua Smith, ... | Tie ⚖️ |
| 40 | Identify candidates with both technical skills and... | complex_combinations | Based on the information provi... | Based on the provided context,... | Deborah Sparks, Pamela Sanchez... | Tie ⚖️ |
| 41 | Find full-stack developers with startup experience... | complex_combinations | I don't know the answer. The i... | Based on the provided context,... | None | Tie ⚖️ |
| 42 | List all candidates suitable for a DevOps role bas... | complex_combinations | Based on the information provi... | Based on the provided context,... | Deborah Sparks, Pamela Sanchez... | GraphRAG ✅ |