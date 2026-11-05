"""
What my test runs. UNIT 8, MILESTONE 3

One scenario per criterion in criteria.md. `run_eval.py` runs each three times.

Criterion 4 (appeal path) can't be a "texts" scenario: it needs a submission
first and then an appeal against the content_id that came back. See the note
at the bottom for how it's tested.

Each text gets its own creator_id (`run_eval.py::bodies_for`), so my 5-per-minute
limit never trips during a run. Scenario names must differ in their first 12
characters or their creator_ids would collide.
"""

SCENARIOS = [
    {
        "name": "own writing",
        "criterion": 1,
        # Criterion 1: of 10 pieces I wrote myself, at most 1 labelled AI.
        # These must be MY OWN writing, plain and formal mixed: 5 biogeography and 3 DCM
        # coursework (formal), a chat message and an email (informal). Names scrubbed.
        "texts": [
            'The figure from Box 6.1 presents a conceptual framework with many parts that helps us better interpret biogeography, its underlying mechanisms, and how they are interrelated to one another.  In order to understand the influences and responses among each entity, there must be a clear definition of the term present followed by examples of how the terms work together to categorize our expectations.  There are several classes of entities, each with their own types',
            'The usefulness of the figure is to understand what happens when one of the fundamental biogeographic processes changes and the responses from other entities.  For example, dispersal is is synonymous with immigration if the organism successfully arrives at a new region and colonizes it by breeding there.  This has a positive correlation with species distribution as seen by the expansion of the organism’s geographic range.',
            'After extinction adaptive radiation takes place, which is one form of an interactive effect.  This is driven by natural selection as in the case of the placental mammals where smaller body sizes did very well following a mass extinction event.  There is another interactive effect where ability for dispersal is enhanced by evolutionary modifications.  This is seen in the example of boxelder fruits, which adapted to look like they have wings so they can be blown far away with wind currents.',
            'The feedback mechanism of the figure occur after different species interact.  The predator-prey interactions between different trophic levels has some plants sustaining a population of herbivores which in turn sustain a population of terrestrial mammalian carnivores.  The zoochory ability of cholla cacti are greatly enhanced by more carnivores and thus more chances for a successful dispersal event resulting in a larger geographic range.',
            'Interactive effects of biogeographic processes are the influence of the fundamental processes on eachother. Distributions and Diversity occur in response to a synthesis of the fundamental geographic processes and variation in habitats to define a species geographic range; Ecological Feedback are the result the ability of co-occurring species to interact; this influences the fundamental biogeographic processes',
            'cardiac cycle is normal in early life, but overtime unstable nuclear lamina of cardiomyocyte causes heart tissue disorganization which decreases ability of ventricles to contract and pump blood to the rest of the body;  the chambers of the ventricles compensate by dilating to increase volume for blood while further weakening heart muscle, this vicious cycle continues to change expressivity of the disease until the ventricular myocardium is fully atrophied in late life.  There is increasing susceptibility to heart attacks for DCM individuals as patient ages and myocardium progressively weakens.',
            'DMD gene encodes for dystrophin which is structural cytoskeletal protein that helps stabilize the cell membrane. Molecular Pathogenesis various types of mutations on the DMD gene can cause XLDCM clinical phenotype such as a deletion in the promoter region of leading to loss-of-function. Cellular Pathogenesis cardiac myocytes deficient in dystrophin are mechanically weak and leads to fragile plasma membranes. Pathophysiology early disease onset for male of around age 10-20 due to unstable cardiomyocyte plasma membrane that progressive worsens upon each contraction leading to end-stage heart failure',
            'Angiotensin II is ahormone that causes constriction of blood vessels for increased blood pressure; formed as part of the RAAS system. ACE inhibitors is for therapy for all patients with reduced ejection fraction; blocks angiotensin-converting-enzyme that converts angiotensin I to angiotensin II. They key point is less angiotensin II lowers blood pressure which reduces load on cardiomyocytes preventing them from stimulated to hypertrophy',
            "What else do people usually say when meeting someone online? :)\nI think I'm a little confused.\nWrite to me what interests you, and I'll be happy to answer your questions.\nAnd please tell me about yourself.\nWhat are your hobbies, what do you like?\nWhat's most important to you in people and women?",
            'Hello <driver-name>,\nThank you for your assistance.\nYes, the large sedan for Ride #1 and medium sedan for Ride #2 are fine.\nMy friend and I have not checked into the <hotel name> yet, that will be tomorrow afternoon and I will email you again once we get the room number via Line.',
        ],
    },
    {
        "name": "spread AI",
        "criterion": 2,
        # Criterion 2: average combined score of these 5 clearly-AI pieces ...
        "texts": [
            'Biogeography is a complex field that examines the distribution of species across space and time. A conceptual framework can help clarify how its core processes relate to one another. By defining key terms clearly and providing illustrative examples, we can better understand the mechanisms that shape where organisms live. Furthermore, recognizing the interconnected nature of these processes is essential for interpreting patterns of biodiversity across different regions and ecosystems.',
            'Dispersal plays a crucial role in determining the geographic distribution of species. When an organism successfully reaches a new region and establishes a breeding population, it contributes to the expansion of its geographic range. This process is closely linked to immigration and colonization. Moreover, changes in dispersal ability can have significant effects on other biogeographic processes, highlighting the importance of understanding how these elements interact within a broader ecological context.',
            "Adaptive radiation is an important evolutionary process that often follows mass extinction events. When many species disappear, surviving lineages can diversify rapidly to fill the available ecological niches. Natural selection drives this diversification, leading to a wide range of new forms and functions. Additionally, evolutionary changes can enhance a species' ability to disperse, which in turn influences its geographic range. These interactive effects demonstrate the dynamic nature of biogeographic processes over time.",
            'Ecological interactions between species play a significant role in shaping biogeographic patterns. Predator-prey relationships across trophic levels can influence population sizes and, consequently, the distribution of organisms. For example, plants that support herbivore populations indirectly sustain the carnivores that depend on them. Furthermore, these feedback mechanisms can affect dispersal opportunities, ultimately influencing the geographic range of species and contributing to the overall diversity of ecosystems.',
            'Habitat variation is a key factor in determining the geographic range of a species. Different environments offer different resources and conditions, which influence where organisms can survive and reproduce. When combined with fundamental processes such as dispersal, speciation, and extinction, these differences contribute to patterns of distribution and diversity. Therefore, a comprehensive understanding of biogeography requires considering both the processes themselves and the environmental context in which they occur.',
        ],
    },
    {
        "name": "spread human",
        "criterion": 2,
        # ... versus these 5 clearly-human pieces (5 of my own writing).
        "texts": [
            'The figure from Box 6.1 presents a conceptual framework with many parts that helps us better interpret biogeography, its underlying mechanisms, and how they are interrelated to one another.  In order to understand the influences and responses among each entity, there must be a clear definition of the term present followed by examples of how the terms work together to categorize our expectations.  There are several classes of entities, each with their own types',
            'The usefulness of the figure is to understand what happens when one of the fundamental biogeographic processes changes and the responses from other entities.  For example, dispersal is is synonymous with immigration if the organism successfully arrives at a new region and colonizes it by breeding there.  This has a positive correlation with species distribution as seen by the expansion of the organism’s geographic range.',
            'After extinction adaptive radiation takes place, which is one form of an interactive effect.  This is driven by natural selection as in the case of the placental mammals where smaller body sizes did very well following a mass extinction event.  There is another interactive effect where ability for dispersal is enhanced by evolutionary modifications.  This is seen in the example of boxelder fruits, which adapted to look like they have wings so they can be blown far away with wind currents.',
            'The feedback mechanism of the figure occur after different species interact.  The predator-prey interactions between different trophic levels has some plants sustaining a population of herbivores which in turn sustain a population of terrestrial mammalian carnivores.  The zoochory ability of cholla cacti are greatly enhanced by more carnivores and thus more chances for a successful dispersal event resulting in a larger geographic range.',
            'Interactive effects of biogeographic processes are the influence of the fundamental processes on eachother. Distributions and Diversity occur in response to a synthesis of the fundamental geographic processes and variation in habitats to define a species geographic range; Ecological Feedback are the result the ability of co-occurring species to interact; this influences the fundamental biogeographic processes',
        ],
    },
    {
        "name": "edited AI",
        "criterion": 3,
        # Criterion 3: the 5 AI texts above (same biogeography topic as my own writing) with about 10% of the words changed.
        "texts": [
            'Biogeography is a complex field that looks at how species are distributed across space and time. A conceptual framework can help show how its core processes relate to each other. By defining key terms clearly and giving examples, we can better understand what shapes where organisms live. It is also essential to recognize how interconnected these processes are when interpreting patterns of biodiversity across regions and ecosystems.',
            'Dispersal plays a crucial role in deciding the geographic distribution of species. When an organism reaches a new region and establishes a breeding population, its geographic range expands. This process is closely linked to immigration and colonization. Changes in dispersal ability can also have big effects on other biogeographic processes, which shows why it matters to understand how these elements interact in a broader ecological context.',
            "Adaptive radiation is an important evolutionary process that often follows mass extinction events. When many species disappear, surviving lineages can diversify quickly to fill the open ecological niches. Natural selection drives this, leading to a wide range of new forms and functions. Evolutionary changes can also boost a species' ability to disperse, which then influences its geographic range. These interactive effects show how dynamic biogeographic processes are over time.",
            'Ecological interactions between species play a big role in shaping biogeographic patterns. Predator-prey relationships across trophic levels can influence population sizes and, as a result, where organisms are found. For example, plants that support herbivore populations indirectly sustain the carnivores that depend on them. These feedback mechanisms can also affect dispersal opportunities, which influences the range of species and the overall diversity of ecosystems.',
            'Habitat variation is a key factor in deciding the geographic range of a species. Different environments offer different resources and conditions, which affect where organisms can survive and reproduce. Combined with fundamental processes like dispersal, speciation, and extinction, these differences contribute to patterns of distribution and diversity. So a full understanding of biogeography means considering both the processes themselves and the environmental context they happen in.',
        ],
    },
    {
        "name": "consistency",
        "criterion": 5,
        # Criterion 5: the same text 5 times; combined score varies by <= 0.05.
        "texts": [
            'Biogeography is a complex field that examines the distribution of species across space and time. A conceptual framework can help clarify how its core processes relate to one another. By defining key terms clearly and providing illustrative examples, we can better understand the mechanisms that shape where organisms live. Furthermore, recognizing the interconnected nature of these processes is essential for interpreting patterns of biodiversity across different regions and ecosystems.',
        ] * 5,
    },
]

# Criterion 4 (appeal path) is tested by hand, not by run_eval.py: submit, take
# the content_id from the response, POST /appeal with it, then read GET /log.


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")
        texts = scenario.get("texts")
        bodies = scenario.get("bodies")
        if texts and bodies:
            problems.append(f"scenario {i} ('{scenario.get('name')}') has both texts and bodies — pick one")
            continue
        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(f"scenario {i}, body {j} is not a dict")
            continue
        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue
        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(f"scenario {i}, text {j} is empty — use 'bodies' for an empty submission")
            elif str(text).startswith("REPLACE ME"):
                problems.append(f"scenario {i} ('{scenario.get('name')}'), text {j} is still the placeholder")
    return problems
