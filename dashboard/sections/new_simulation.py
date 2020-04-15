import streamlit as st

from ..simulation import Simulation

import numpy as np

#np.random.binomial(n, p, 1000)


def run(tr):
    simulation = Simulation()

    simulation.add_state("Susceptible")
    simulation.add_state("Asymptomatic")
    simulation.add_state("Symptomatic")
    simulation.add_state("Recovered")
    simulation.add_state("Dead")
    simulation.add_state("Positive")

    def alive(d):
        return starting_population - d["Dead"]

    starting_population = st.sidebar.number_input(
        "Population", 0, 100, 10
    ) * 1000000

    # people getting sick
    st.sidebar.markdown("### Infection dynamics")

    n_meet = st.sidebar.slider("People meeting", 0, 100, 10)
    n_test = st.sidebar.slider("Tests per day", 0, 10000, 1000)
    p_n_test = st.sidebar.slider("Percent(%) of Tests apply to Syntomatic", 0, 100, 80, format='%d%%')
    p_infect_asymptomatic = st.sidebar.slider(
        "Probability of infection from asymptomatic", 0.0, 1.0, 0.1
    )
    p_infect_symptomatic = st.sidebar.slider(
        "Probability of infection from symptomatic", 0.0, 1.0, 0.2
    )

    def temp(d):
        r = d["Asymptomatic"] \
            * n_meet \
            * p_infect_asymptomatic \
            * d['Susceptible'] \
            // alive(d)
        #print(r, alive(d),  d['Susceptible'], d["Asymptomatic"], d["Asymptomatic"]*n_meet*p_infect_asymptomatic/alive(d))
        return r

    simulation.add_transition(
        "Susceptible",
        "Asymptomatic",
        temp
        # lambda d: (
        #     d["Asymptomatic"]
        #     * n_meet
        #     * p_infect_asymptomatic
        #     * d['Susceptible']
        #     // alive(d)
        # ),
    )
    simulation.add_transition(
        "Susceptible",
        "Asymptomatic",
        lambda d: (
            d["Symptomatic"]
            * n_meet
            * p_infect_symptomatic
            * d['Susceptible']
            // alive(d)
        ),
    )

    simulation.add_transition(
        "Asymptomatic",
        "Positive",
        lambda d: (
            min(
                d['Asymptomatic']*n_test*(100-p_n_test)//(100*alive(d)),
                 d['Asymptomatic']
            )
        ),
    )

    simulation.add_transition(
        "Symptomatic",
        "Positive",
        lambda d: (
            min(
                d['Symptomatic'],
                n_test*p_n_test//100
            )
        ),
    )

    # people developing symptoms and disease
    st.sidebar.markdown("### Disease evolution")

    p_symptoms = st.sidebar.slider(
        "Chance of developing symptoms (daily)", 0.0, 1.0, 0.1
    )
    p_asympt_recover = st.sidebar.slider(
        "Chance of recovering for asymptomatic patients (daily)", 0.0, 1.0, 0.2
    )
    p_sympt_dead = st.sidebar.slider(
        "Chance of dying for symptomatic patients (daily)", 0.0, 1.0, 0.05
    )
    p_sympt_recover = st.sidebar.slider(
        "Chance of recovering for symptomatic patients (daily)", 0.0, 1.0, 0.1
    )

    simulation.add_transition("Asymptomatic", "Symptomatic", p_symptoms)
    simulation.add_transition("Asymptomatic", "Recovered", p_asympt_recover)
    simulation.add_transition("Symptomatic", "Dead", p_sympt_dead)
    simulation.add_transition("Symptomatic", "Recovered", p_sympt_recover)
    simulation.add_transition("Positive", "Dead", p_sympt_dead)
    simulation.add_transition("Positive", "Recovered", p_sympt_recover)

    data = simulation.run(
        80, Susceptible=starting_population, Asymptomatic=1
    ).astype(int)

    data["Sick"] = data["Asymptomatic"] + data["Symptomatic"]
    data["New dead"] = data["Dead"].diff().fillna(0)
    data["Letality"] = data["New dead"] / data["Sick"]
    data["Letality (smooth)"] = data['Letality'].rolling(10).mean()
    data["Sum"] = data["Sick"]+data['Dead']+data['Susceptible']+data['Recovered']+data['Positive']
    data = data[data["Sick"] > 0]

    visualize = list(data.columns)
    visualize = st.multiselect("Columns to visualize", visualize, ["Asymptomatic", "Symptomatic", "Dead"])

    st.line_chart(data[visualize])

    st.write(starting_population)
    st.write(data)

    # st.write("### Simulation using binomial sampling with the selected probabilities")

    simulation = Simulation()

    simulation.add_state("Susceptible")
    simulation.add_state("Asymptomatic")
    simulation.add_state("Symptomatic")
    simulation.add_state("Recovered")
    simulation.add_state("Dead")
    simulation.add_state("Positive")

    # def temp2(d):
    #     print(alive(d),  d['Susceptible'], d["Symptomatic"], d["Symptomatic"]*n_meet*p_infect_symptomatic/alive(d))
    #     r = round(np.random.binomial(d['Susceptible'], d["Symptomatic"]*n_meet*p_infect_symptomatic/alive(d), 1000).mean())
    #     print(r)
    #     return r

    simulation.add_transition(
        "Susceptible",
        "Asymptomatic",
        lambda d: (
            round(np.random.binomial(d['Susceptible'], d["Asymptomatic"]*n_meet*p_infect_asymptomatic/alive(d), 1000).mean())
        ),
    )

    simulation.add_transition(
        "Susceptible",
        "Asymptomatic",
        # temp2
        lambda d: (
            round(np.random.binomial(d['Susceptible'], d["Symptomatic"]*n_meet*p_infect_symptomatic/alive(d), 1000).mean())
        )
    )

    # simulation.add_transition(
    #     "Asymptomatic",
    #     "Positive",
    #     lambda d: (
    #         min(
    #             round(np.random.binomial(n_test*(100-p_n_test)//100,d['Asymptomatic']/alive(d), 1000).mean()),
    #             d['Asymptomatic']
    #         )
    #     ),
    # )

    simulation.add_transition(
        "Symptomatic",
        "Positive",
        lambda d: (
            min(
                d['Symptomatic'],
                n_test*p_n_test//100
            )
        ),
    )

    simulation.add_transition("Asymptomatic", "Symptomatic", p_symptoms)
    simulation.add_transition("Asymptomatic", "Recovered", p_asympt_recover)
    simulation.add_transition("Symptomatic", "Dead", p_sympt_dead)
    simulation.add_transition("Symptomatic", "Recovered", p_sympt_recover)
    simulation.add_transition("Positive", "Dead", p_sympt_dead)
    simulation.add_transition("Positive", "Recovered", p_sympt_recover)

    # data = simulation.run(
    #     80, Susceptible=starting_population, Asymptomatic=1
    # ).astype(int)

    # data["Sick"] = data["Asymptomatic"] + data["Symptomatic"]
    # data["New dead"] = data["Dead"].diff().fillna(0)
    # data["Letality"] = data["New dead"] / data["Sick"]
    # data["Letality (smooth)"] = data['Letality'].rolling(10).mean()
    # data["Sum"] = data["Sick"]+data['Dead']+data['Susceptible']+data['Recovered']+data['Positive']
    # data = data[data["Sick"] > 0]

    # visualize = list(data.columns)
    # visualize = st.multiselect("Columns to visualize", visualize, ["Asymptomatic", "Symptomatic", "Dead"], key="Columns to visualize2")

    # st.line_chart(data[visualize])


    # st.write("### Visualizing the graphical model")

    # graph = simulation.graph()
    # st.write(graph)
    # st.write(starting_population)
    # st.write(data)