from robot.motorController import MotorController, messageHeader, MESSAGES
import unittest
from unittest import mock
import math

class TestMotorController(unittest.TestCase):

    def setUp(self):
        self.serialConn = mock.MagicMock()
        self.controller = MotorController(0, self.serialConn, 1)

    def test_command(self):
        self.controller.command(.4)
        self.assertEqual(self.controller.getCommand(), .4)
        self.serialConn.queueMsg.assert_called_once_with(messageHeader.pack(1, MESSAGES.oMotorCommand.value[0]) + MESSAGES.oMotorCommand.value[1].pack(0, 102), 0)
        self.controller.command(-.8)
        self.assertEqual(self.controller.getCommand(), -.8)
        self.serialConn.queueMsg.assert_called_with(messageHeader.pack(1, MESSAGES.oMotorCommand.value[0]) + MESSAGES.oMotorCommand.value[1].pack(1, 204), 0)

    def test_queryPosition(self):
        pass

    def test_queryDeltaPos(self):
        pass

    def test_receivePosition(self):
        self.controller._position = 0
        self.controller._receiveFeedback(b"\x01\x03\x39\x30")
        self.assertAlmostEqual(self.controller._position, 3.5910149, places=5)

    def test_receiveDeltaPos(self):
        self.controller._deltaPosition = 0
        self.controller._receiveFeedback(b"\x01\x02\x15\xcD\x5B\x07")#075BCD15
        self.assertAlmostEqual(self.controller._deltaPosition, 35912.1241999, places=5)

if __name__ == '__main__':
    unittest.main()