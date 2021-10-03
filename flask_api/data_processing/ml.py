import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import SGDClassifier
import joblib
import os
from sklearn.neural_network import MLPClassifier
import time


leagues = {
    "Spain": "historic/SP1.csv",
    "England": "historic/E0.csv",
    "France": "historic/F1.csv",
    "Italy": "historic/I1.csv",
    "Germany": "historic/D1.csv"
}

def normalize_team_names(column, dataset, fname):
    """
    Team names need to be converted from labels to numbers to make
    it work for sklearn (LabelEncoder is not possible since the normalization
    needs to be done against different naming conventions
    - e. g. Man United in the csv file vs Manchester United used
    by UnibetAPI causes issues)
    - in contrary to the method in main.py, this method requires to normalize team
    names in the dataset
    """
    filename = "teams/" + fname + ".txt"
    for row in range(len(dataset[column])):
        line_num = 1
        with open(filename) as uniform_team_names:
            for line in uniform_team_names:
                if dataset.iloc[row, dataset.columns.get_loc(column)] in line:
                    break
                line_num += 1
            dataset.iloc[row, dataset.columns.get_loc(column)] = line_num
    return dataset

def save_results(filename, content):
    """
    Append content to a specified filename
    """
    with open(filename, 'a+') as file:
        file.write(content + "\n")


class DataPreparation:
    def __init__(self):
        """
        - self.data are used as information which is provided to the ML model
        -  self.target is the expected result (based on real data)
        concerning self.data
        """
        self.data = None
        self.target = None


    def prepare_data(self, data, fname):
        """
        Waits until historic are downloaded,
        then loads prepared csv file in order to prepare dataset
        for the machine learning models
        - labels - team names need to be normalized to numbers
        """
        while not os.path.exists(data):
            print("here")
            time.sleep(1)
        dataset = pd.read_csv(data, header=None)
        dataset.columns = dataset.iloc[0]
        dataset = dataset[1:]
        dataset = dataset.dropna() #no NaN rows
        dataset = normalize_team_names("HomeTeam", dataset, fname)
        dataset = normalize_team_names("AwayTeam", dataset, fname)
        #dataset = dataset.apply(label_enc.fit_transform)
        # 1 home team, 2 away team, 8-10 Bet365 odds
        self.data = dataset.iloc[:, [1,2,8,9,10]]
        self.target = dataset.iloc[:, 11]  # result
        return (self.data, self.target)


    def prepare_all_models(self):
        """
        In the directory models, the method prepares for each league a model
        """
        if not(os.path.exists("models")):
            os.mkdir("models")
        for fname, path in leagues.items():
            data, target = self.prepare_data(path, fname)
            support_vector_machine(data, target, fname)
            decision_tree(data, target, fname)
            knearest_neighbours(data, target, fname)
            logistic_regression(data, target, fname)
            random_forest(data, target, fname)
            gradient_boosting(data, target, fname)
            stochastic_gradient_descent(data, target, fname)
            multilevel_perceptron(data, target, fname)

    def run_accuracy_rate(self, iterations):
        """
        Accuracy rate - not called within the application
        - only for measurement purposes
        -- for each league the user can specify number of iterations which are written in the results directory
        and the results average for each league and each ML model is displayed in the output
        - potentially for parameter tuning for ML models used in the application
        or choosing different ML models etc.
        """
        start = time.time()
        print("Accuracy rate test")
        if not(os.path.exists("results")):
            os.makedirs("results")
        for fname, path in leagues.items():
            svm_count = dtree_count = knn_count = logr_count = gradb_count = randf_count = sgd_count = mlperc_count = 0
            data, target = self.prepare_data(path, fname)
            for _ in range(iterations):
                svm_acc = support_vector_machine(data, target, fname, False)
                svm_count += svm_acc

                dtree_acc = decision_tree(data, target, fname, False)
                dtree_count += dtree_acc

                knn_acc = knearest_neighbours(data, target, fname, False)
                knn_count += knn_acc

                logr_acc = logistic_regression(data, target, fname, False)
                logr_count += logr_acc

                randf_acc = random_forest(data, target, fname, False)
                randf_count += randf_acc

                gradb_acc = gradient_boosting(data, target, fname, False)
                gradb_count += gradb_acc

                sgd_acc = stochastic_gradient_descent(data, target, fname, False)
                sgd_count += sgd_acc

                mlperc_acc = multilevel_perceptron(data, target, fname, False)
                mlperc_count += mlperc_acc
                
                #SAVE
                save_results("results/{}svm.txt".format(fname), str(svm_acc))
                save_results("results/{}dtree.txt".format(fname),  str(dtree_acc))
                save_results("results/{}knn.txt".format(fname), str(knn_acc))
                save_results("results/{}randf.txt".format(fname),  str(randf_acc))
                save_results("results/{}gradb.txt".format(fname),  str(gradb_acc))
                save_results("results/{}logr.txt".format(fname),  str(logr_acc))
                save_results("results/{}sgd.txt".format(fname),  str(sgd_acc))
                save_results("results/{}mlperc.txt".format(fname),  str(mlperc_acc))
            print("For fname: ", fname)
            print("Support vector machine: ", svm_count / iterations)
            print("Decision Tree: ", dtree_count / iterations)
            print("K-nearest neighbours: ", knn_count / iterations)
            print("Logistic regression: ", logr_count / iterations)
            print("Random forest: ", randf_count / iterations)
            print("Gradient Boosting: ",  gradb_count / iterations)
            print("Stochastic Gradient Descent: ", sgd_count / iterations)
            print("Multilevel perceptron: ", mlperc_count / iterations)
        end = time.time()
        print("Process took: ", end - start, " seconds")

def sklearn_predict(clf, data, target):
    """
    Dataset train-test separation,
    model training and model testing
    - outputs decimal number [0,1] how accurate the model was
    """
    X_train, X_test, y_train, y_test = train_test_split(data, target, test_size=0.33)
    trained_clf = clf.fit(X_train, y_train)
    predicted_list = trained_clf.predict(X_test)
    expected_list = y_test
    return accuracy_score(expected_list, predicted_list)


def save_model(clf, league, method):
    """
    Creates a specified model in pkl format for a particular league
    """
    joblib.dump(clf, "models/{}{}.pkl".format(method, league))


def load_model(fname, method):
    """
    Load previously trained and tested model
    """
    model = joblib.load(
        "models/{}{}.pkl".format(method, fname.partition(".")[0])
    )
    return model
    
def decision_tree(data, target, fname, save=True):
    """
    https://www.datacamp.com/community/tutorials/decision-tree-classification-python
    Prediction of result using decision tree machine learning model - classifier
    - partitions input space into regions where each of the regions is solved with a simpler model
    - criterion - (by default dtree uses gini - Gini index), entropy - information gain 
    - max_depth - the deeper the tree, the fitter model (and more complex rules for decision)
    - min_samples_split - minimum number of samples to split an internal node
    - returns prediction accuracy
    """
    clf = tree.DecisionTreeClassifier(criterion="entropy", max_depth=4, min_samples_split=10)
    prediction_acc = sklearn_predict(clf, data, target)
    if save:
        save_model(clf, fname, "dtree")
    return prediction_acc

def knearest_neighbours(data, target, fname, save=True):
    """
    https://www.datacamp.com/community/tutorials/k-nearest-neighbor-classification-scikit-learn
    Learning based on the k nearest neighbors - user's choice of k is crucial in order to work well on the data provided
    - n_neigbors - key parameter - find n nearest neighbors of a point
    - leaf_size - leaf size pased to the main knn algorithm (optimal value needed to be foudnd via GridSearchCV - 30 is default)
    - p - use of mannhattan distance as a metric
    - returns prediction accuracy
    """
    clf = KNeighborsClassifier(n_neighbors=100, leaf_size=10, p=1)
    prediction_acc = sklearn_predict(clf, data, target)
    if save:
        save_model(clf, fname, "knn")  
    return prediction_acc

def logistic_regression(data, target, fname, save=True):
    """
    Probabilistic approach - uses logistic function to calculate proabability
    - gives the output based on certain independent variables
    - max_iter - maximum number of iterations needed to be enlarged since the model
    could not converge within the default limit
    - returns prediction accuracy
    """
    clf = LogisticRegression(max_iter=1000)
    prediction_acc = sklearn_predict(clf, data, target)
    if save:
        save_model(clf, fname, "logr")  
    return prediction_acc

def support_vector_machine(data, target, fname, save=True):
    """
    https://www.datacamp.com/community/tutorials/svm-classification-scikit-learn-python
    - SVM constructs a hyperplane in multidimensional space to separate different classes from each other
    - choice of parameters - https://scikit-learn.org/stable/auto_examples/svm/plot_rbf_parameters.html
    - returns prediction accuracy
    """
    clf = svm.SVC(gamma=0.01, kernel="rbf")
    prediction_acc = sklearn_predict(clf, data, target)
    if save:
        save_model(clf, fname, "svm")  
    return prediction_acc

def random_forest(data, target, fname, save=True):
    """
    Estimator which fits a number of decision tree classifiers on subsamples of dataset
    - averages to improve prediction accuracy
    - choice of parameters https://towardsdatascience.com/hyperparameter-tuning-the-random-forest-in-python-using-scikit-learn-28d2aa77dd74
    - returns prediction accuracy
    """
    clf = RandomForestClassifier(min_samples_split=20, n_estimators=1000,max_features="sqrt",max_depth=20)
    prediction_acc = sklearn_predict(clf, data, target)
    if save:
        save_model(clf, fname, "randf")  
    return prediction_acc

def gradient_boosting(data, target, fname, save=True):
    """
    Fitting using gradient descent algorithm - to find a local minimum of a differentiable function
    - choice of parameters https://medium.com/all-things-ai/in-depth-parameter-tuning-for-gradient-boosting-3363992e9bae
    - returns prediction accuracy
    """
    clf = GradientBoostingClassifier(learning_rate=0.01, min_samples_split=2, max_depth=2)
    prediction_acc = sklearn_predict(clf, data, target)
    if save:
        save_model(clf, fname, "gradb")  
    return prediction_acc

def stochastic_gradient_descent(data, target, fname, save=True):
    """
    Stochastic approximation of gradient descent
    - choice of parameters https://scikit-learn.org/stable/auto_examples/model_selection/plot_randomized_search.html
    - returns prediction accuracy
    """
    clf = SGDClassifier(average=True, alpha=0.1)
    prediction_acc = sklearn_predict(clf, data, target)
    if save:
        save_model(clf, fname, "sgd")  
    return prediction_acc

def multilevel_perceptron(data, target, fname, save=True):
    """
    Multilevel perceptron relies on an underlying neural network for classification
    - choice of parameters https://datascience.stackexchange.com/questions/36049/how-to-adjust-the-hyperparameters-of-mlp-classifier-to-get-more-perfect-performa
    - returns prediction accuracy
    """
    clf = MLPClassifier(max_iter=1000,hidden_layer_sizes=30,activation="logistic",alpha=0.00001)
    prediction_acc = sklearn_predict(clf, data, target)
    if save:
        save_model(clf, fname, "mlperc")
    return prediction_acc

if __name__ == "__main__":
    dprep = DataPreparation()
    if not os.path.exists("models"):
        os.makedirs("models")
    #dprep.prepare_all_models()
    dprep.run_accuracy_rate(iterations=10)
