import logging
import time

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.utils import Bunch

from budgery.db import crud, models
from budgery.user import User

LOGGER = logging.getLogger(__name__)
TRANSACTION_CATEGORY_MODEL = "transaction-category-model.joblib"

def _categorized_transaction_bunch(db: crud.Session) -> Bunch:
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

async def train_transaction_categorizor(
		db: crud.Session,
		user: User,
	) -> None:
	"Trains the transaction categorizor, saves the model for later inference."
	start = time.time()
	bunch = _categorized_transaction_bunch(db)

	tfidf_vectorizer = TfidfVectorizer()
	train_tfidf = tfidf_vectorizer.fit_transform(bunch.data)
	clf = MultinomialNB().fit(train_tfidf, bunch.target)
	LOGGER.info("Trained transaction categorization model in %s seconds", time.time() - start)
	
	joblib.dump((tfidf_vectorizer, clf, bunch.target_names), TRANSACTION_CATEGORY_MODEL)

def transaction_category(transaction: models.Transaction) -> str:
	tfidf_vectorizer, clf, target_names = joblib.load(TRANSACTION_CATEGORY_MODEL)
	to_categorize = [transaction.description]
	new_tfidf = tfidf_vectorizer.transform(to_categorize)
	predicted = clf.predict(new_tfidf)

	return target_names[predicted[0]]
