FROM python:3.9.18

# Set the working directory
RUN mkdir -p /raven
RUN mkdir -p /raven/src
RUN mkdir -p /raven/tests

# Copy the current directory contents into the container at /raven
WORKDIR /raven
COPY Makefile requirements.txt /raven/
COPY src /raven/src
COPY tests /raven/tests

# Move the main test file to the Root directory
RUN mv /raven/tests/test_raven.py /raven/test_raven.py

# Install any needed packages specified in requirements.txt
RUN pip3 install -r requirements.txt

# Run RAVEN tests
CMD ["make", "test-run"]