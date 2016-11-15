import os
#Takes in the file name, returns a dict of weighted edges. Each key i s a 2 tuple of the two teams with the first one alphabetically first the value is how much the first team in the key won the series by (games that is).
def read_file(f_name):
    f=open(f_name,'r')
    edges={}
    first=True
    for line in f:
        if line.strip()=='':
            continue
        line=line.strip().split(',')
        team1=line[4]
        team2=line[6]
        if team1=='Tm':
            continue
        if team1<team2:
            t=team1
            team1=team2
            team2=t
        win=(line[7].strip()=='W')
        if win:
            win=-1
        else:
            win=1
        edges[(team1,team2)]=edges.get((team1,team2),0)+win
        edges[(team2,team1)]=edges.get((team2,team1),0)-win
    #    return [(t1,t2,edges[(t1,t2)]) for t1,t2 in edges]
    return edges
def read_folder(folder_name):
    edges={}
    teams=[]
    for f in os.listdir(folder_name):
        teams.append(f.split('_')[1])
        edges.update(read_file(folder_name+'/'+f))
    return (teams,edges)

if __name__=='__main__':
    (teams,edges)=read_folder('data/mlb/2015')
    print len(teams)
    print len(edges)
