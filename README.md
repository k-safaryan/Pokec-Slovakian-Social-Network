# Pokec-Slovakian-Social-Network

## Project Overview
This project implements a **mini database system** for the Pokec social network dataset (~1.6M users, ~30M connections), featuring:

- **Indexed search** using AVL trees for efficient attribute queries (e.g., age).
- **Graph traversal** for pathfinding from any user to the network root (CEO).
- **Basic analytics** for data distribution (gender, education, languages, music preferences).
- **Scalable design** for large datasets.

Built with **Python 3** and **Streamlit** for interactive UI.

---

## Project Structure

```
project/
│
├─ data/
│   └─ dataset.csv
│
├─ core/
│   ├─ __init__.py
│   ├─ graph.py
│   ├─ indexing.py
│   ├─ query_engine.py
│   └─ storage.py
│
├─ ui/
│   └─ app.py
│
├─ main.py
├─ report.pdf
└─ README.md
```


## Dataset overview

Pokec (http://pokec.azet.sk/) is the most popular on-line social network in Slovakia. The popularity of network has  not changed even after the coming of Facebook. Pokec has been provided for more than 10 years and connects more than 1.6 million people. Datasets contains anonymized data of the whole network. Profile data contains gender, age, hobbies, interest, education etc. Profile data are in Slovak language. Friendships in Pokec are oriented.

**Dataset statistics**

* Nodes 1,632,803
* Edges 30,622,564
* Nodes in largest WCC 1632803 (1.000)
* Edges in largest WCC 30622564 (1.000)
* Nodes in largest SCC 1304537 (0.799)
* Edges in largest SCC 29183655 (0.953)


