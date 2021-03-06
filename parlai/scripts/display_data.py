#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""
Basic example which iterates through the tasks specified and prints them out. Used for
verification of data loading and iteration.

For example, to make sure that bAbI task 1 (1k exs) loads one can run and to
see a few of them:

Examples
--------

.. code-block:: shell

  python display_data.py -t babi:task1k:1
"""

from parlai.core.params import ParlaiParser
from parlai.agents.repeat_label.repeat_label import RepeatLabelAgent
from parlai.core.worlds import create_task
from parlai.utils.strings import colorize
from parlai.scripts.script import ParlaiScript

import random


def setup_args(parser=None):
    if parser is None:
        parser = ParlaiParser(True, True, 'Display data from a task')
    # Get command line arguments
    parser.add_argument('-n', '-ne', '--num-examples', type=int, default=10)
    parser.add_argument('-mdl', '--max-display-len', type=int, default=1000)
    parser.add_argument('--display-ignore-fields', type=str, default='agent_reply')
    parser.add_argument(
        '-v',
        '--display-verbose',
        default=False,
        action='store_true',
        help='If false, simple converational view, does not show other message fields.',
    )

    parser.set_defaults(datatype='train:ordered')
    return parser


def simple_display(opt, world, turn):
    if opt['batchsize'] > 1:
        raise RuntimeError('Simple view only support batchsize=1')
    act = world.get_acts()[0]
    if turn == 0:
        text = "- - - NEW EPISODE: " + act.get('id', "[no agent id]") + " - - -"
        print(colorize(text, 'highlight'))
    text = act.get('text', '[no text field]')
    print(colorize(text, 'text'))
    labels = act.get('labels', act.get('eval_labels', ['[no labels field]']))
    labels = '|'.join(labels)
    print('   ' + colorize(labels, 'labels'))


def display_data(opt):
    # force ordered data to prevent repeats
    if 'ordered' not in opt['datatype']:
        opt['datatype'] = opt['datatype'].split(':')[0] + ':ordered'

    # create repeat label agent and assign it to the specified task
    agent = RepeatLabelAgent(opt)
    world = create_task(opt, agent)

    # Show some example dialogs.
    turn = 0
    for _ in range(opt['num_examples']):
        world.parley()

        # NOTE: If you want to look at the data from here rather than calling
        # world.display() you could access world.acts[0] directly, see simple_display above.
        if opt['display_verbose']:
            print(world.display() + '\n~~')
        else:
            simple_display(opt, world, turn)
            turn += 1
            if world.get_acts()[0]['episode_done']:
                turn = 0

        if world.epoch_done():
            print('EPOCH DONE')
            break

    try:
        # print dataset size if available
        print(
            '[ loaded {} episodes with a total of {} examples ]'.format(
                world.num_episodes(), world.num_examples()
            )
        )
    except Exception:
        pass


class DisplayData(ParlaiScript):
    @classmethod
    def setup_args(cls):
        return setup_args()

    def run(self):
        return display_data(self.opt)


if __name__ == '__main__':
    random.seed(42)
    DisplayData.main()
