import tensorflow as tf


class ARIMA:

    def calc_ARIMA(self):

        self.logger.info("Performing ARIMA analysis for %s", self.symbol)

        return 1


# Initialize two constants
x1 = tf.constant([1, 2, 3, 4])
x2 = tf.constant([5, 6, 7, 8])

# Multiply
result = tf.multiply(x1, x2)
# Intialize the Session
# sess = tf.Session()

# # Print the result
# print(sess.run(result))

# # Close the session
# sess.close()
