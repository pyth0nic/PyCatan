from pycatan.board import Board
from pycatan.hex import Hex
from pycatan.point import Point
from pycatan.hex_type import HexType
from pycatan.harbor import Harbor, HarborType

import math
import random

# The default, hexagonal board filled with random hexes and tokens
class DefaultBoard(Board):

    def __init__(self, game):
        super(DefaultBoard, self).__init__(game)

        # Set hexes
        hex_deck = Board.get_shuffled_hex_deck()
        token_deck = Board.get_shuffled_hex_nums()
        temp_hexes = []
        for r in range(5):
            temp_hexes.append([])
            for i in range([3, 4, 5, 4, 3][r]):
                # Add a hex
                new_hex = Hex(type=hex_deck.pop(), token_num=None, position=[r, i], points=[])
                temp_hexes[-1].append(new_hex)
                # Remove the token if it is the desert
                if new_hex.type == HexType.DESERT:
                    self.robber = [r, i]
                else:
                    new_hex.token_num = token_deck.pop()

        self.hexes = tuple(map(lambda x: tuple(x), temp_hexes))

        # Add points
        temp_points = []
        for r in range(6):
            temp_points.append([])
            for i in range([7, 9, 11, 11, 9, 7][r]):
                point = Point(hexes=[], position=[r, i])
                temp_points[-1].append(point)
                # Set point/hex relations
                for pos in DefaultBoard.get_hex_indexes_for_point(r, i):
                    point.hexes.append(self.hexes[pos[0]][pos[1]])
                    self.hexes[pos[0]][pos[1]].points.append(point)

        self.points = tuple(map(lambda x: tuple(x), temp_points))

        # adds harbors
        # each harbor is around the edge of the board
        # and are separated by n points, when n is a pattern of 2 3 2 repeating
        # so this gets all the points in segments of top, right, left, bottom
        # and then adds them together
        top = []
        bottom = []

        # the index of the last row
        last = len(self.points) - 1

        # adds the points
        for i in range(len(self.points[0])):
            top.append([0, i])
            bottom.append([last, len(self.points[0]) - 1 - i])

        # adds all the points on the right and left
        right = []
        left = []

        for r in range(1, len(self.points) - 1):
            length = len(self.points[r]) - 1

            # orders the points depending if they are on the top half or bottom half
            if r < (len(self.points) - 1) / 2:
                right.append([r, length - 1])
                right.append([r, length])

                left.append([len(self.points) - 1 - r, 1])
                left.append([len(self.points) - 1 - r, 0])

            else:
                right.append([r, length])
                right.append([r, length - 1])

                left.append([len(self.points) - 1 - r, 0])
                left.append([len(self.points) - 1 - r, 1])

        outside_points = []
        outside_points.extend(top)
        outside_points.extend(right)
        outside_points.extend(bottom)
        outside_points.extend(left)

        # adds a harbor for each points in the pattern 2 3 2 2 3 2 etc

        # the index of the outside point to build a harbor on
        index = 0
        # the count of harbors build
        count = 0
        # the pattern of spaces between harbors
        pattern = [2, 3, 2]
        # the different types of harbors
        harbor_types = [
            HarborType.WOOD,
            HarborType.BRICK,
            HarborType.ORE,
            HarborType.WHEAT,
            HarborType.SHEEP,
            HarborType.ANY,
            HarborType.ANY,
            HarborType.ANY,
            HarborType.ANY
        ]

        # shuffles the harbors
        random.shuffle(harbor_types)
        # goes around the board once and adds harbors
        while index < len(outside_points):

            # creates a new harbor
            harbor = Harbor(point_one=outside_points[index], point_two=outside_points[index + 1], type=harbor_types[count])
            # adds it to harbors
            self.harbors.append(harbor)
            # increments index by the next pattern, adds one to fit with the width of each harbor being 2
            index += pattern[count % 3] + 1
            # adds one to count
            count += 1

        # puts the robber on the desert hex to start
        for r in range(len(temp_hexes)):
            # checks if this row has the desert
            if temp_hexes[r].count(HexType.DESERT) > 0:
                # places the robber
                self.robber = [r, temp_hexes[r].index(HexType.DESERT)]

    # Returns the indexes of the hexes connected to a certain points
    # on the default, hexagonal Catan board
    @staticmethod
    def get_hex_indexes_for_point(r, i):
        # the indexes of the hexes
        hex_indexes = []
        # Points on a hexagonal board
        points = [
            [None] * 7,
            [None] * 9,
            [None] * 11,
            [None] * 11,
            [None] * 9,
            [None] * 7
        ]
        # gets the adjacent hexes differently depending on whether the point is in the top or the bottom
        if r < len(points) / 2:
            # gets the hexes below the point ------------------

            # adds the hexes to the right
            if i < len(points[r]) - 1:
                hex_indexes.append([r, math.floor(i / 2)])

            # if the index is even, the number is between two hexes
            if i % 2 == 0 and i > 0:
                hex_indexes.append([r, math.floor(i / 2) - 1])

            # gets the hexes above the point ------------------

            if r > 0:
                # gets the hex to the right
                if i > 0 and i < len(points[r]) - 2:
                    hex_indexes.append([r - 1, math.floor((i - 1) / 2)])

                # gets the hex to the left
                if i % 2 == 1 and i < len(points[r]) - 1 and i > 1:
                    hex_indexes.append([r - 1, math.floor((i - 1) / 2) - 1])

        else:

            # adds the below -------------

            if r < len(points) - 1:
                # gets the hex to the right or directly below
                if i < len(points[r]) - 2 and i > 0:
                    hex_indexes.append([r, math.floor((i - 1) / 2)])

                # gets the hex to the left
                if i % 2 == 1 and i > 1 and i < len(points[r]):
                    hex_indexes.append([r, math.floor((i - 1) / 2 - 1)])

            # gets the hexes above ------------

            # gets the hex above and to the right or directly above
            if i < len(points[r]) - 1:
                hex_indexes.append([r - 1, math.floor(i / 2)])

            # gets the hex to the left
            if i > 1 and i % 2 == 0:
                hex_indexes.append([r - 1, math.floor((i - 1) / 2)])

        return hex_indexes

    # gets the points that are connected to the point given
    def get_connected_points(self, r, i):

        # the connected points
        connected_points = []
        # whether the point has another point directly above or directly below
        has_point_above = False

        # half of the last index
        # if the board has 6 rows, this will be 2.5
        # so that ceiling/flooring will give the two middle rows
        half_height = (len(self.points) - 1) / 2

        # if it is in the top half
        if r < half_height:

            # even points have a point below, odd points have one above
            if i % 2 == 0:

                # adds a point below

                if r == math.floor(half_height):
                    # this connection has the same index because it is crossing over the middle
                    connected_points.append([r + 1, i])

                else:
                    connected_points.append([r + 1, i + 1])

            else:
                # adds a point above
                if r > 0 and i > 0:
                    connected_points.append([r - 1, i - 1])

        # if it is in the bottom half
        else:
            if i % 2 == 0:

                # adds a point above
                if r == math.ceil(half_height):
                    # same index because it is crossing the middle
                    connected_points.append([r - 1, i])

                else:
                    connected_points.append([r - 1, i + 1])

            else:

                # adds a point below
                if r < len(self.points) - 1 and i > 0:
                    connected_points.append([r + 1, i - 1])

        # # The different in index
        # #
        # #          ABOVE   | BELOW
        # # TOP    |   -1    |   +1
        # # BOTTOM |   +1    |   -1

        # gets the adjacent points
        if i > 0:
            connected_points.append([r, i - 1])

        if i < len(self.points[r]) - 1:
            connected_points.append([r, i + 1])

        return connected_points