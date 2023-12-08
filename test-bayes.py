from sklearn.datasets import load_iris
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.utils import Bunch

from budgery.db import crud, models
from budgery.db.connection import connect, session
from starlette.config import Config

def all_transaction_descriptions(db):
	all_transactions = crud.transaction_list(db)
	return [t.description for t in all_transactions]

def categorized_transaction_bunch(db) -> Bunch:
	transactions = crud.transaction_list_with_category(db)
	data = []
	target = []
	target_names = []
	categories_to_id = {}
	index = 0
	for transaction in transactions:
		category_id = categories_to_id.get(transaction.category)
		if category_id is None:
			categories_to_id[transaction.category] = index
			category_id = index
			target_names.append(transaction.category)
			index += 1
		data.append(transaction.description)
		target.append(category_id)

	bunch = Bunch(
		data=data,
		target=target,
		target_names=target_names,
	)
	return bunch

def main() -> None:
	config = Config("env")
	engine = connect(config)
	db = session(engine)
	all_descriptions = all_transaction_descriptions(db)

	bunch = categorized_transaction_bunch(db)

	#count_vectorizer = CountVectorizer()
	#train_count_vector = count_vectorizer.fit_transform(all_descriptions)
	#tfidf_transformer = TfidfTransformer()
	#train_tfidf = tfidf_transformer.fit_transform(all_descriptions)

	tfidf_vectorizer = TfidfVectorizer()
	train_tfidf = tfidf_vectorizer.fit_transform(bunch.data)


	clf = MultinomialNB().fit(train_tfidf, bunch.target)
	print("trained")

	uncategorized_transactions = crud.transaction_list(
		db=db,
		category="None",
		limit=10,
	)
	to_categorize = [t.description for t in uncategorized_transactions][:20]
	new_tfidf = tfidf_vectorizer.transform(to_categorize)
	predicted = clf.predict(new_tfidf)

	for doc, category in zip(to_categorize, predicted):
		print(f"{doc} => {bunch.target_names[category]}")
	return


	#X, y = load_iris(return_X_y=True)
	data = load_iris()
	import pdb;pdb.set_trace()
	# X is a numpy.ndarray(shape=(150, 4), dtype=float64)
	# y is a numpy.ndarray(shape=(150,), dtype=int64
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=0)
	gnb = GaussianNB()
	y_pred = gnb.fit(X_train, y_train).predict(X_test)
	print("Number of mislabeled points out of a total %d points : %d"
		  % (X_test.shape[0], (y_test != y_pred).sum()))

if __name__ == "__main__":
	main()
