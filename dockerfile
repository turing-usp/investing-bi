FROM public.ecr.aws/lambda/python:3.7

WORKDIR /var/task

COPY requirements.txt requirements.txt

# Needed packages for cvxpy (pyportfolioopt requirement)
RUN yum -y install gcc gcc-c++

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["app.lambda_handler"]

