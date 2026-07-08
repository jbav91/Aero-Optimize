import pandas as pd
import pulp

# 1. Simulated Standby Crew Database
standby_crew_data = {
    'Crew_ID': ['P1', 'P2', 'P3', 'CP1', 'CP2', 'CP3', 'FA1', 'FA2', 'FA3', 'FA4', 'FA5'],
    'Role': ['Pilot', 'Pilot', 'Pilot', 'Co-Pilot', 'Co-Pilot', 'Co-Pilot', 'Attendant', 'Attendant', 'Attendant', 'Attendant', 'Attendant'],
    'Cost_Per_Hour': [200, 250, 220, 150, 160, 140, 50, 60, 45, 55, 65],
    'Max_Hours_Left': [4, 8, 12, 10, 5, 8, 12, 4, 9, 10, 6]
}
crew_df = pd.DataFrame(standby_crew_data)

def assign_standby_crew(flight_duration_hours=7, crew_pool=crew_df):
    """
    Calculates the cheapest legal crew combination for a delayed flight.
    """
    # Initialize the Optimization Problem
    prob = pulp.LpProblem("Minimize_Crew_Cost", pulp.LpMinimize)

    # Create Decision Variables (Binary: 0 = Not Selected, 1 = Selected)
    crew_vars = pulp.LpVariable.dicts("Assign", crew_pool['Crew_ID'], cat='Binary')

    # Objective Function: Minimize Total Hourly Cost
    prob += pulp.lpSum([crew_vars[row['Crew_ID']] * row['Cost_Per_Hour'] for index, row in crew_pool.iterrows()])

    # Constraint A: Minimum Staffing Requirements (1 Pilot, 1 Co-Pilot, 2 Attendants)
    prob += pulp.lpSum([crew_vars[row['Crew_ID']] for index, row in crew_pool.iterrows() if row['Role'] == 'Pilot']) == 1
    prob += pulp.lpSum([crew_vars[row['Crew_ID']] for index, row in crew_pool.iterrows() if row['Role'] == 'Co-Pilot']) == 1
    prob += pulp.lpSum([crew_vars[row['Crew_ID']] for index, row in crew_pool.iterrows() if row['Role'] == 'Attendant']) == 2

    # Constraint B: Legal Working Hours (Cannot assign if the flight exceeds their max hours left)
    for index, row in crew_pool.iterrows():
        prob += crew_vars[row['Crew_ID']] * flight_duration_hours <= row['Max_Hours_Left']

    # Solve the Problem
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    # Extract Results
    if pulp.LpStatus[prob.status] != 'Optimal':
        return {"Status": "Failed", "Message": "No valid crew combination found (Not enough legal hours in standby pool)."}

    selected_crew = []
    total_cost = 0
    for index, row in crew_pool.iterrows():
        if crew_vars[row['Crew_ID']].varValue == 1.0:
            selected_crew.append(row['Crew_ID'])
            total_cost += row['Cost_Per_Hour']

    return {
        'Status': pulp.LpStatus[prob.status],
        'Selected_Crew': selected_crew,
        'Total_Hourly_Cost': total_cost
    }


# Example: XGBoost predicts a delay. The flight routing takes 7 hours.
if __name__ == "__main__":
    result = assign_standby_crew()
    print(result)