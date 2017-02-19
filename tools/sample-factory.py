from types import TypeType


class ECOTest(object):
    @classmethod
    def execute(self):
        pass

    @classmethod
    def collect_logs(self):
        pass

    @classmethod
    def analyze_results(self):
        pass


class TestCase1(ECOTest):
    @classmethod
    def collect_logs(self):
        print "Collecting logs for test case 1"

    @classmethod
    def analyze_results(self):
        print "Analyzing logs for test case 1"

    @classmethod
    def execute(self):
        print "Executing test case 1"


class TestCase2(ECOTest):
    @classmethod
    def execute(self):
        print "Executing test case 2"

    @classmethod
    def collect_logs(self):
        print "Collecting logs for test case 2"

    @classmethod
    def analyze_results(self):
        print "Analyzing logs for test case 2"


class TestCase3(ECOTest):
    @classmethod
    def execute(self):
        print "Executing test case 3"

    @classmethod
    def collect_logs(self):
        print "Collecting logs for test case 3"

    @classmethod
    def analyze_results(self):
        print "Analyzing logs for test case 3"


class TestFactory(object):
    @classmethod
    def runTests(self):
        testClasses =  [j for (i, j) in globals().iteritems() if isinstance(j, TypeType) and issubclass(j, ECOTest)]
        for testClass in testClasses:
            testClass.execute()
            testClass.collect_logs()
            testClass.analyze_results()
            print "\n"


def main():
    testFactory = TestFactory.runTests()

if __name__ == "__main__":
    main()