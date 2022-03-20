import requests

if __name__ == "__main__":

	# note that <CLIENT_ID> refers to 'personal use script' and <SECRET_TOKEN> to 'token'
	auth = requests.auth.HTTPBasicAuth('<CLIENT_ID>', '<SECRET_TOKEN>')

	# here we pass our login method (password), <USERNAME>, and <PASSWORD>
	data = {'grant_type': 'password',
	        'username': '<USERNAME>',
	        'password': '<PASSWORD>'}

	# setup our header info, which gives reddit a brief description of our app
	headers = {'User-Agent': 'ContestCounter/1.0.0'}

	# send our request for an OAuth token
	res = requests.post('https://www.reddit.com/api/v1/access_token',
	                    auth=auth, data=data, headers=headers)

	# convert response to JSON and pull access_token value
	TOKEN = res.json()['access_token']

	# add authorization to our headers dictionary
	headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

	# while the token is valid (~2 hours) we just add headers=headers to our requests
	requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)

	# fetch all the posts in the subreddit
	res_posts = requests.get("https://oauth.reddit.com/r/serendipitempo/new.json?limit=1000", headers=headers)

	scores = {}
	for post in res_posts.json()['data']['children']:
		post_id = post['data']['id']
		# fetch all the comments in the post
		res_comments = requests.get(f"http://oauth.reddit.com/comments/{post_id}?sort=old&threaded=false", headers=headers)
		for comment in res_comments.json()[1]['data']['children']:
			# collect the total score and the total number of comments in the subreddit for each active user
			if comment['data']['author'] in scores:
				scores[comment['data']['author']]['total_score'] += comment['data']['score']
				scores[comment['data']['author']]['total_comments'] += 1
			else:
				scores[comment['data']['author']] = {'total_score': comment['data']['score'], 'total_comments': 1}
	scores_sorted = dict(sorted(scores.items(), key=lambda item: (item[1]['total_score'], item[1]['total_comments']), reverse=True))
	i = 0
	# print a leaderboard of users who have the highest score and the highest number of comments
	for score in scores_sorted:
		i += 1
		print(f"{i}. {score}: {scores_sorted[score]['total_score']} punt{'o' if scores_sorted[score]['total_score']==1 else 'i'} con {scores_sorted[score]['total_comments']} comment{'o' if scores_sorted[score]['total_comments']==1 else 'i'}")
