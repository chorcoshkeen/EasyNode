import pickle 
class coin(object):
    def __init__(self, coin_name, config_file, configfolder, daemon, cli, repo, port):                      #add_date, website, discord
        self.name = coin_name
        self.config_file = config_file
        self.configfolder = configfolder
        self.daemon = daemon 
        self.cli = cli 
        self.repo = repo
        self.port = port
        #self.add_date = add_date
        #self.website = website
        #self.discord = discord 
        #self.explorer = explorer
def read_coins(tab):
    try:
        f = open(tab + "_coins.dat", "rb")
        coinsz = pickle.load(f)
    except:
        f = open(tab + "_coins.dat", "wb")
        coinsz = []
    f.close()
    return coinsz

def add_coin(added_coin, tab):
    coins = read_coins(tab)
    coins.append(added_coin)
    f = open(tab + "_coins.dat", "wb")
    pickle.dump(coins, f)
    f.close()

def del_coin(deleted_coin):
    new_coins = []
    coinsz = read_coins(tab = "abu")
    for i in coinsz:
        if i.name == deleted_coin:
            pass
        else:
            new_coins.append(i)
    f = open("abu_coins.dat", "wb")
    pickle.dump(new_coins, f)
    f.close()
    
    
    