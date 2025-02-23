FROM python:3.9.21

# Set the working directory
RUN mkdir -p /raven
RUN mkdir -p /raven/src
RUN mkdir -p /raven/tests

# Copy the current directory contents into the container at /raven
WORKDIR /raven
COPY Makefile dev-requirements.txt /raven/
COPY src /raven/src
COPY library /raven/library
COPY tests /raven/tests

# Install any needed packages specified in requirements.txt
RUN pip3 install -r dev-requirements.txt

# Run RAVEN tests
CMD ["make", "test-run"]