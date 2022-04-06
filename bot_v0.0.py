from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
from sc2.position import Point2
from sc2.ids.unit_typeid import UnitTypeId

from numpy.random import seed, randint
# deque is a better implementation of lists, for pop to have a complexity of O(1) instead of 0(n)
from collections import deque


def save_data_to_file():
    pass


MEMORY = [0, 0, 0, 0]
DEST_POSITIONS = []
BOOL_INIT_FORMATION = False
BOOL_COMPUTE_ALL_4_POINTS = False
BOOL_MAIN_SPLIT = False
# RANDOM_RESULTS = randint(0, 10, 10).tolist()
LOOPING_ID = 0


class WorkerRushBot(BotAI):
    async def on_start(self):
        self.client.game_step = 2


    async def on_step(self, iteration: int):
        global MEMORY, BOOL_INIT_FORMATION, BOOL_COMPUTE_ALL_4_POINTS, BOOL_MAIN_SPLIT, DEST_POSITIONS, RANDOM_RESULTS
        global LOOPING_ID
        positions_results = None
        print(f"{iteration=}")

        if not self.townhalls.ready:
            # Attack with all workers if we don't have any nexuses left, attack-move on enemy spawn (doesn't work on 4 player map) so that probes auto attack on the way
            for worker in self.workers:
                worker.attack(self.enemy_start_locations[0])
            return
        else:
            nexus = self.townhalls.ready.random

        # Make probes until we have 16 total
        if nexus.is_idle:
            if self.can_afford(UnitTypeId.PROBE):
                nexus.train(UnitTypeId.PROBE)

        # If we have no pylon, build one near starting nexus
        if not self.structures(UnitTypeId.PYLON) and self.already_pending(UnitTypeId.PYLON) == 0:
            if self.can_afford(UnitTypeId.PYLON):
                await self.build(UnitTypeId.PYLON, near=nexus)

        if not BOOL_COMPUTE_ALL_4_POINTS:
            # not the good place
            await self.compute_all_4_points(self.start_location)

        if not BOOL_INIT_FORMATION:
            await self.bool_compute_action("initial formation")

        if iteration == 10 and BOOL_COMPUTE_ALL_4_POINTS:
            for worker, dest in zip(MEMORY, DEST_POSITIONS):
                worker.move(dest)

        if iteration > 15:
            random_coord_index = randint(0, 4)
            random_id_worker = randint(0, 11)
            self.workers[random_id_worker].move(DEST_POSITIONS[LOOPING_ID])
            LOOPING_ID = (LOOPING_ID + 1) % 4
            print(f"{random_id_worker=} goes to place: {LOOPING_ID=}")

        print("------------------------------------------------")

    async def bool_compute_action(self, action_to_compute: str):
        global MEMORY, BOOL_INIT_FORMATION
        desty = self.start_location.y - 5

        # fill memory
        for i, worker in enumerate(self.workers):
            if i < 4:
                MEMORY[i] = worker
                BOOL_INIT_FORMATION = True

            # worker.move(Point2((self.start_location.x, desty)))

    async def compute_all_4_points(self, center_position: Point2):
        global BOOL_COMPUTE_ALL_4_POINTS, DEST_POSITIONS
        # Order is like a Clock. Top, Right, Bot, Left
        res = []
        radius = 5
        # Top
        DEST_POSITIONS.append(Point2((center_position.x, center_position.y + radius)))
        # Right
        DEST_POSITIONS.append(Point2((center_position.x + radius, center_position.y)))
        # Bot
        DEST_POSITIONS.append(Point2((center_position.x, center_position.y - radius)))
        # Left
        DEST_POSITIONS.append(Point2((center_position.x - radius, center_position.y)))
        BOOL_COMPUTE_ALL_4_POINTS = True
        return res


if __name__ == "__main__":
    seed(1)
    run_game(maps.get("Abyssal Reef LE"), [
        Bot(Race.Protoss, WorkerRushBot()),
        Computer(Race.Protoss, Difficulty.Medium)
    ], realtime=True)
