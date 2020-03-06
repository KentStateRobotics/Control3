COMP = gcc
COMP_ARGS = -Wall -std=c++11 -c
LINK = gcc
LINK_ARGS = -Wall -o

FILES = motorController.o
TESTS = testMotorController

tests: $(TESTS)
	./$?
	clean

test%: %.o $(TESTS) $(FILES)
	$(LINK) $< $(LINK_ARGS)

%.o: %.cpp
	$(COMP) $< $(COMP_ARGS)


clean:
	rm -f *.o
	rm -f $(TESTS) $(FILES)