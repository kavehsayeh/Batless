import os, random, zipfile, urllib.request
import matplotlib.pyplot as plt

def parseSchedule(playerID, year):
    """
    returns a pitch-by-pitch summary of every plate appearances for the given
    player in the given year.
    """
    # retrieve the folder of events from the appropriate season
    # a team's event file includes only its home games, so we'll need all of them
    url = 'https://www.retrosheet.org/events/{}eve.zip'.format(year)
    with urllib.request.urlopen(url) as f:
        with open('events.zip', 'wb') as output:
            output.write(f.read())
    with zipfile.ZipFile('events.zip', 'r') as zip_ref:
        zip_ref.extractall('events')
    os.remove('events.zip')

    directory = os.fsencode('events')
    plateAppearances=[]

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith('.EVN') or filename.endswith('.EVA'):
            source = open('events/{}'.format(filename), 'r')
            schedule = source.readlines()
            source.close()
            # pull out just plays from the player we're interested in
            for line in schedule:
                plateAppearances
                if playerID in line and 'play' in line:
                    plateAppearances.append(line.strip().split(','))

    # plateAppearances is a list of lists, each list detailing one play:
    # index 0: identifies the line as recording a play, not another event like
    # a substitution (redundant)
    # index 1: inning
    # index 2: 0 for visitors/top of the inning; 1 for home/bottom of the inning
    # index 3: player ID (first 4 letters of last name, first initial, sequential
    # number) (redundant)
    # index 5: pitch-by-pitch rundown of the plate appearance up to the play
    # index 6: the play

    # if a play occurs mid-plate appearance (for example, a stolen base), the
    # plate appearance will be split across multiple lines. Fortunately, the
    # pitch-by-pitch for the entire plate appearance always appears in the last
    # line, so we can just delete all but the last line of each plate appearance.

    # eliminates lines with NP ("no play") in the event column
    plateAppearances = [pa for pa in plateAppearances if pa[6] != 'NP']

    # eliminates lines where the pitch-by-pitch summary is the same as the
    # beginning of the pitch-by-pitch summary of the next line (+ a period,
    # which Retrosheet uses to denote non-pitch events)
    droppedPlateAppearances = []
    for i in range(len(plateAppearances)-1):
        if plateAppearances[i][5] + '.' not in plateAppearances[i+1][5]:
            droppedPlateAppearances.append(plateAppearances[i])

    return droppedPlateAppearances

def pa_sim(pa, ball_rate_swing, ball_rate_all):
    """
    Takes in a Retrosheet pitch-by-pitch summary of a plate appearance and
    simulates how that plate appearance would go without a bat.
    ball_rate_swing: chance that a pitch was outside, given that the batter swung.
    ball_rate_all: chance that any given pitch was outside.
    """
    balls = 0
    strikes = 0
    out_return_value = 0
    walk_return_value = 1
    for pitch in pa:
        if pitch in "H":        # hit batter
            return walk_return_value
        elif pitch in "BIP":    # ball/intentional ball/pitchout
            balls += 1
        elif pitch in "C":      # called strike
            strikes += 1
        elif pitch in "FSLTX":  # foul/swinging strike/foul bunt/tip/in play
            if random.random() <= ball_rate_swing: 
                balls += 1
            else:
                strikes += 1

        if strikes == 3:
            break
        elif balls == 4:
            return walk_return_value
        
    while strikes < 3 and balls < 4:
        if random.random() <= ball_rate_all: 
            balls += 1
        else:
            strikes += 1
        if balls == 4:
            return walk_return_value

    return out_return_value

if __name__ == "__main__":
    playerID = 'bondb001'
    year = 2004
    
    season = parseSchedule(playerID, year)
    PAs = len(season)
    trials = 3000

    OBPtrials = []
    for i in range(trials):
        onbase = 0
        for pa in season:
            onbase += pa_sim(pa[5], 0.191, 0.587)
        OBPtrials.append(onbase/PAs)
    meanOBP = sum(OBPtrials)/len(OBPtrials)
    
    plt.hist(OBPtrials, 20)
    plt.axvline(meanOBP, color='r', linestyle='dashed', linewidth=1)
    plt.xlabel('OBP (mean: {})'.format(round(meanOBP, 4)))
    plt.ylabel('Frequency')
    plt.title('Histogram of OBP without bat')
    plt.savefig('OBPdist.png')
    plt.show()
