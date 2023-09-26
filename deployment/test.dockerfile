FROM python:3.9.18

# Set the working directory
RUN mkdir -p /raven

# Copy the current directory contents into the container at /raven
WORKDIR /raven
COPY . /raven

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Run RAVEN tests
CMD ["make", "test-run"]