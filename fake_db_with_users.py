from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, ToyNames, Inventory, User

engine = create_engine('sqlite:///appwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Dummy User
User1 = User(name='Jperry', email='jrp0801@yahoo.com',
             picture='https://pbs.twimg.com/profile_images/400x400.png')
session.add(User1)
session.commit()

# Adding Toys to ToyNames Table
paw_patrol = ToyNames(user_id='1', name='Paw Patrol')
session.add(paw_patrol)
session.commit()

pj_masks = ToyNames(user_id='1', name='PJ Masks')
session.add(pj_masks)
session.commit()

board_games = ToyNames(user_id='1', name='Board Games')
session.add(board_games)
session.commit()

game_consoles = ToyNames(user_id='1', name='Game Consoles')
session.add(game_consoles)
session.commit()


# Adding Paw Patrol toy descriptions to Inventory table
paw_patrol1 = Inventory(user_id='1', name='Paw Patrol Mighty Tower',
                        id='100',
                        description='Super Pups defending Adventure Bay',
                        toynames=paw_patrol)
session.add(paw_patrol1)
session.commit()

paw_patrol2 = Inventory(user_id='1', name='Paw Patrol Sea Partol',
                        id='101',
                        description='Pups on Sea Patrol', toynames=paw_patrol)
session.add(paw_patrol2)
session.commit()

paw_patrol3 = Inventory(user_id='1', name='Paw Patrol Lookout Tower',
                        id='102',
                        description='Pups on patrol', toynames=paw_patrol)
session.add(paw_patrol3)
session.commit()

pj_masks1 = Inventory(user_id='1', name='PJ Masks PJ Seeker',
                      id='200', description='PJ Seeker', toynames=pj_masks)
session.add(pj_masks1)
session.commit()

pj_masks2 = Inventory(user_id='1', name='PJ HQ',
                      id='201',
                      description='PJ Masks Headquarters', toynames=pj_masks)
session.add(pj_masks2)
session.commit()

board_games1 = Inventory(user_id='1', name='Lazer Maze Puzzle Game',
                         id='300',
                         description='Puzzle strategy game',
                         toynames=board_games)
session.add(board_games1)
session.commit()

game_consoles1 = Inventory(user_id='1', name='Sega Genesis',
                           id='400',
                           description='Sega Genesis Game Console',
                           toynames=game_consoles)
session.add(game_consoles1)
session.commit()

game_consoles2 = Inventory(user_id='1', name='Sega Saturn',
                           id='401',
                           description='Sega Saturn Game Console',
                           toynames=game_consoles)
session.add(game_consoles2)
session.commit()

game_consoles3 = Inventory(user_id='1', name='Playstation 1',
                           id='402',
                           description='PSX Console', toynames=game_consoles)
session.add(game_consoles3)
session.commit()

game_consoles4 = Inventory(user_id='1', name='Playstation 2',
                           id='403',
                           description='PS2 Console', toynames=game_consoles)
session.add(game_consoles4)
session.commit()

game_consoles5 = Inventory(user_id='1', name='Playstation 3',
                           id='404',
                           description='PS3 Console', toynames=game_consoles)
session.add(game_consoles5)
session.commit()

print "Added Kids Toys!"
