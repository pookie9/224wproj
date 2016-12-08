import os

def read_folder(folderName):
    """
    Processes the MLB CSV files located in folderName

    Args:
        folderName: the relative filepath to the CSV directory

    Returns:
        teams: a list of the team names
        edges: a dictionary of (team1, team2) -> w/l where w/l is the number of times
            team 1 beat team 2 minus the number of times team 2 beat team 1
    """
    edges = {}
    teams = []
    for filename in os.listdir(folderName):
        teams.append(filename.split('_')[1])
        filepath = folderName + "/" + filename
        edges.update(read_file(filepath))
    return teams, edges

def read_file(filename):
    """
    Processes the CSV file located as filename

    Args:
        filename: the relative filepath to the CSV file

    Returns:
        edges: a dictionary of (team1, team2) -> w/l as described above
    """
    f = open(filename, 'r')
    edges = {}
    for line in f:
        line = line.strip()
        if line == '':
            continue

        lineComponents = line.split(",")
        team1 = lineComponents[4]
        team2 = lineComponents[6]

        if team1 == "Tm":
            continue

        win = 1 if "W" in lineComponents[7] else -1
        edges[(team1, team2)] = edges.get((team1, team2), 0) + win
    return edges

if __name__=='__main__':
    (teams,edges)=read_folder('data/mlb/2015')
    print len(teams)
    print len(edges)
