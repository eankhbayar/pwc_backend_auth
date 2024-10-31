const AWS = require('aws-sdk');

const rekognition = new AWS.Rekognition();

const handler = async (event, context) => {
	console.log("Verify Auth Challenge: " + JSON.stringify(event));
	let userPhoto = '';
	event.response.answerCorrect = false;

	// Searching existing faces indexed on Rekognition using the provided photo on S3
	const objectName = event.request.challengeAnswer;
	const params = {
		CollectionId: process.env.COLLECTION_NAME,
		Image: {
			S3Object: {
				Bucket: process.env.BUCKET_SIGN_IN,
				Name: objectName
			}
		},
		MaxFaces: 1,
		FaceMatchThreshold: 90
	};

	console.log(params);

	try {
		const data = await rekognition.searchFacesByImage(params).promise();

		// Evaluates if Rekognition was able to find a match with the required 
		// confidence threshold
		if (data.FaceMatches[0]) {
			console.log('Face Id: ' + data.FaceMatches[0].Face.FaceId);
			console.log('Similarity: ' + data.FaceMatches[0].Similarity);
			userPhoto = data.FaceMatches[0].Face.FaceId;

			if (userPhoto && event.request.privateChallengeParameters.answer === userPhoto) {
				event.response.answerCorrect = true;
			}
		}
	} catch (err) {
		console.error("Unable to query. Error:", JSON.stringify(err, null, 2));
		throw err;
	}

	return event;
};

exports.handler = handler;
