import unittest
import sys
sys.path.insert(0, './')
from ProjectClassifier import classify_project
from ProjectClassifier import get_naive_base_classified_result

class ClassifierTestCase(unittest.TestCase):
    '''
     Test for ProjectClassifier
     
    '''
    def test_classification(self):
        self.assertEquals(classify_project('Atom', 'The Hackable editor.', language='CofeeScript'), "IDE")
    
    def test_naivebayes_classification(self):
        self.assertEquals(get_naive_base_classified_result('Atom' + " " +'The Hackable editor.'+ " " +'CofeeScript'), "IDE")
        self.assertEquals(get_naive_base_classified_result('bootstrap'+ " " + 'The most popular HTML , CSS , and JavaScript framework for developing responsive, mobile first projects on the web.'+  " "+'CSS'), "CSS")
        
if __name__=='__main__':
    unittest.main()
