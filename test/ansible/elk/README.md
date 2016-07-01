# Instructions for running the testcases to verify the elk playbook install

Edit vars.yml with the elastic search ip address and port

**ansible-playbook elk_test.yml -i "localhost ansible_connection=local,"**
