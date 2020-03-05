from robot.motorController import MotorController, messageHeader, MESSAGES
import unittest
from unittest import mock

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


if __name__ == '__main__':
    unittest.main()