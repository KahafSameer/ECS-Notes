# AWS ECS Practical Exercises and Scenarios

## Table of Contents
1. Getting Started - Basic Setup
2. Exercise 1: Deploy Your First Container on Fargate
3. Exercise 2: Deploy Container on EC2 Launch Type
4. Exercise 3: Multi-Container Task with Communication
5. Exercise 4: Memory Management and Troubleshooting
6. Exercise 5: Accessing and Debugging Containers
7. Exercise 6: Log Configuration and Troubleshooting
8. Real-World Scenarios and Solutions
9. Practice Challenges

---

## Prerequisites

### What You Need:
1. AWS Account (Free tier is sufficient)
2. Basic understanding of Docker
3. A simple application to containerize (we'll provide examples)
4. AWS Console access

### Recommended Setup:
- Use AWS Free Tier to minimize costs
- Clean up resources after each exercise
- Take notes of any errors you encounter

---

## Exercise 1: Deploy Your First Container on Fargate

### Objective
Learn how to deploy a simple web application using Fargate (serverless containers).

### Scenario
You have a simple web application and want to deploy it without managing servers.

### Step-by-Step Instructions

#### Part A: Create a Simple Docker Image

**Option 1: Use Pre-built Image**
We'll use a simple nginx web server: `nginx:latest`

**Option 2: Create Your Own (Optional)**
Create a simple HTML page and Dockerfile.

#### Part B: Push Image to Amazon ECR (Elastic Container Registry)

**Step 1: Create ECR Repository**
1. Go to AWS Console → ECR (Elastic Container Registry)
2. Click "Create repository"
3. Repository name: `my-first-app`
4. Leave other settings as default
5. Click "Create repository"

**Step 2: Push Image (If using custom image)**
1. Click on your repository
2. Click "View push commands"
3. Follow the commands shown (authenticate, tag, push)

**For this exercise, we'll use public nginx image, so skip pushing.**

#### Part C: Create ECS Cluster

**Step 1: Create Cluster**
1. Go to ECS Console
2. Click "Clusters" → "Create Cluster"
3. Cluster name: `my-first-cluster`
4. Leave "AWS Fargate (serverless)" selected
5. Click "Create"

#### Part D: Create Task Definition

**Step 1: Create Task Definition**
1. Go to ECS → Task Definitions
2. Click "Create new task definition"
3. Task definition family: `my-web-app`
4. Launch type: Select "AWS Fargate"

**Step 2: Configure Task**
1. Operating system: Linux
2. Task size:
   - CPU: 0.25 vCPU
   - Memory: 0.5 GB
3. Task role: Leave empty for now
4. Task execution role: Create new role (or use existing)

**Step 3: Add Container**
1. Click "Add container"
2. Container name: `nginx`
3. Image URI: `nginx:latest`
4. Port mappings:
   - Container port: 80
   - Protocol: TCP
5. Memory limits:
   - Hard limit: 512 MB
   - Soft limit: 256 MB

**Step 4: Configure Logging**
1. Scroll to "Log configuration"
2. Check "Auto-configure CloudWatch Logs"
3. Log group: `/ecs/my-web-app`

**Step 5: Create**
1. Click "Add" (to add container)
2. Click "Create" (to create task definition)

#### Part E: Create and Run Service

**Step 1: Create Service**
1. Go to your cluster: `my-first-cluster`
2. Click "Services" tab
3. Click "Create"

**Step 2: Configure Service**
1. Launch type: Fargate
2. Task definition: `my-web-app` (latest)
3. Service name: `my-web-service`
4. Number of tasks: 1
5. Deployment type: Rolling update

**Step 3: Configure Network**
1. VPC: Select default VPC
2. Subnets: Select at least 2 subnets
3. Security group: Create new
   - Add rule: HTTP (port 80) from Anywhere (0.0.0.0/0)
4. Public IP: ENABLED (important!)

**Step 4: Load Balancer (Optional for now)**
- Skip load balancer for this exercise

**Step 5: Create Service**
1. Review settings
2. Click "Create"

#### Part F: Access Your Application

**Step 1: Find Task Public IP**
1. Go to your cluster
2. Click "Tasks" tab
3. Click on your running task
4. Find "Public IP" in the details
5. Copy the IP address

**Step 2: Access in Browser**
1. Open browser
2. Go to: `http://<public-ip>`
3. You should see nginx welcome page!

### What You Learned
- ✓ Created ECS cluster
- ✓ Created task definition with Fargate
- ✓ Configured container memory
- ✓ Set up CloudWatch logging
- ✓ Deployed a service
- ✓ Accessed running container

### Practice Questions
1. What happens if you set number of tasks to 3?
2. Can you access the container without public IP?
3. What happens if you stop the task manually?

---

## Exercise 2: Deploy Container on EC2 Launch Type

### Objective
Learn how to deploy containers on EC2 instances and understand the infrastructure.

### Scenario
You want more control over the infrastructure and ability to SSH into instances.

### Step-by-Step Instructions

#### Part A: Create ECS Cluster with EC2

**Step 1: Create Cluster**
1. Go to ECS Console → Clusters
2. Click "Create Cluster"
3. Cluster name: `my-ec2-cluster`
4. Infrastructure: Select "Amazon EC2 instances"

**Step 2: Configure Infrastructure**
1. Provisioning model: On-Demand
2. EC2 instance type: `t2.micro` (free tier)
3. Desired capacity: 1 instance
4. SSH key pair: Select your key pair (or create new)
5. VPC: Default VPC
6. Subnets: Select subnets
7. Security group: Create new
   - Allow SSH (port 22) from your IP
   - Allow HTTP (port 80) from anywhere

**Step 3: Create Cluster**
1. Review settings
2. Click "Create"
3. Wait for cluster creation (2-3 minutes)

#### Part B: Verify EC2 Instance

**Step 1: Check ECS Instances**
1. Go to your cluster
2. Click "ECS Instances" tab
3. You should see 1 instance
4. Note the instance ID

**Step 2: Check EC2 Console**
1. Go to EC2 Console → Instances
2. Find your instance (search by instance ID)
3. Note the public IP address

#### Part C: Create Task Definition for EC2

**Step 1: Create Task Definition**
1. Go to ECS → Task Definitions
2. Click "Create new task definition"
3. Task definition family: `my-ec2-app`
4. Launch type: Select "Amazon EC2"

**Step 2: Add Container**
1. Click "Add container"
2. Container name: `web`
3. Image: `nginx:latest`
4. Memory limits:
   - Hard limit: 256 MB
   - Soft limit: 128 MB
5. Port mappings:
   - Host port: 80
   - Container port: 80
6. Log configuration:
   - Auto-configure CloudWatch Logs
   - Log group: `/ecs/my-ec2-app`

**Step 3: Create**
1. Click "Add"
2. Click "Create"

#### Part D: Run Task

**Step 1: Run Task**
1. Go to your cluster: `my-ec2-cluster`
2. Click "Tasks" tab
3. Click "Run new task"

**Step 2: Configure**
1. Launch type: EC2
2. Task definition: `my-ec2-app`
3. Number of tasks: 1
4. Click "Create"

#### Part E: Access Container

**Step 1: Via Browser**
1. Get EC2 instance public IP
2. Open browser: `http://<ec2-public-ip>`
3. See nginx welcome page

**Step 2: Via SSH**
1. SSH to EC2 instance:
```bash
ssh -i your-key.pem ec2-user@<ec2-public-ip>
```

2. List containers:
```bash
docker ps
```

3. Access container:
```bash
docker exec -it <container-id> /bin/bash
```

4. Inside container:
```bash
# Check nginx is running
ps aux | grep nginx

# View nginx config
cat /etc/nginx/nginx.conf

# Exit container
exit
```

### What You Learned
- ✓ Created EC2-based ECS cluster
- ✓ Understood EC2 instance management
- ✓ SSH access to instances
- ✓ Docker commands on EC2
- ✓ Direct container access

### Practice Questions
1. What's the difference in accessing Fargate vs EC2 containers?
2. Can you run multiple tasks on the same EC2 instance?
3. What happens if the EC2 instance stops?

---

## Exercise 3: Multi-Container Task with Communication

### Objective
Learn how containers in the same task communicate with each other.

### Scenario
You have a web application that needs a Redis cache. Both should run in the same task.

### Step-by-Step Instructions

#### Part A: Create Multi-Container Task Definition

**Step 1: Create Task Definition**
1. Go to ECS → Task Definitions
2. Click "Create new task definition"
3. Task definition family: `web-with-redis`
4. Launch type: Fargate
5. Task size:
   - CPU: 0.5 vCPU
   - Memory: 1 GB

**Step 2: Add Redis Container**
1. Click "Add container"
2. Container name: `redis`
3. Image: `redis:latest`
4. Port mappings:
   - Container port: 6379
5. Memory limits:
   - Hard limit: 256 MB
   - Soft limit: 128 MB
6. Log configuration: Auto-configure
7. Click "Add"

**Step 3: Add Web Application Container**
1. Click "Add container" again
2. Container name: `web`
3. Image: `nginx:latest` (for demo)
4. Port mappings:
   - Container port: 80
5. Memory limits:
   - Hard limit: 512 MB
   - Soft limit: 256 MB
6. Environment variables:
   - Name: `REDIS_HOST`
   - Value: `localhost`
   - Name: `REDIS_PORT`
   - Value: `6379`
7. Log configuration: Auto-configure
8. Click "Add"

**Step 4: Create Task Definition**
1. Click "Create"

#### Part B: Run the Task

**Step 1: Create Service**
1. Go to your Fargate cluster
2. Create new service
3. Task definition: `web-with-redis`
4. Service name: `web-redis-service`
5. Number of tasks: 1
6. Configure networking (enable public IP)
7. Create service

#### Part C: Verify Communication

**Step 1: Use ECS Exec to Access Web Container**
1. Enable ECS Exec on service (update service)
2. Get task ID from tasks tab
3. Use AWS CLI:
```bash
aws ecs execute-command \
    --cluster my-first-cluster \
    --task <task-id> \
    --container web \
    --interactive \
    --command "/bin/bash"
```

**Step 2: Test Redis Connection**
Inside the web container:
```bash
# Install redis-cli (if not present)
apt-get update && apt-get install -y redis-tools

# Test connection to Redis
redis-cli -h localhost -p 6379 ping
# Should return: PONG

# Set a value
redis-cli -h localhost -p 6379 set mykey "Hello from web container"

# Get the value
redis-cli -h localhost -p 6379 get mykey
# Should return: "Hello from web container"
```

**Step 3: Access Redis Container**
```bash
aws ecs execute-command \
    --cluster my-first-cluster \
    --task <task-id> \
    --container redis \
    --interactive \
    --command "/bin/sh"
```

Inside Redis container:
```bash
# Connect to Redis
redis-cli

# Check the value set from web container
get mykey
# Should return: "Hello from web container"
```

### What You Learned
- ✓ Created multi-container task
- ✓ Configured container communication via localhost
- ✓ Used environment variables
- ✓ Tested inter-container connectivity
- ✓ Used ECS Exec for debugging

### Practice Questions
1. Can containers in different tasks communicate via localhost?
2. What happens if Redis container crashes?
3. How would you add a third container?

---

## Exercise 4: Memory Management and Troubleshooting

### Objective
Understand memory limits and handle memory-related issues.

### Scenario
Your application is crashing due to memory issues. Learn to diagnose and fix.

### Step-by-Step Instructions

#### Part A: Create Task with Low Memory

**Step 1: Create Task Definition**
1. Task definition family: `memory-test`
2. Launch type: Fargate
3. Task memory: 0.5 GB (512 MB)
4. Add container:
   - Name: `app`
   - Image: `nginx:latest`
   - Hard limit: 512 MB
   - Soft limit: 256 MB

#### Part B: Simulate Memory Issue

**Step 1: Create Task with Insufficient Memory**
1. Create another revision
2. Keep task memory: 0.5 GB
3. Set container hard limit: 600 MB (more than task memory)
4. Try to create - you'll get an error!

**Error Message**:
```
The container memory + overhead exceeds the task memory
```

**What This Teaches**:
- Task memory must be ≥ sum of container hard limits
- Always leave headroom for system overhead

#### Part C: Test Memory Limits

**Step 1: Create Proper Task Definition**
1. Task definition: `memory-stress-test`
2. Task memory: 1 GB
3. Container:
   - Name: `stress`
   - Image: `progrium/stress`
   - Command: `--vm 1 --vm-bytes 400M --vm-hang 0`
   - Hard limit: 512 MB
   - Soft limit: 256 MB

**Step 2: Run Task**
1. Run the task
2. Watch what happens
3. Task should run successfully (400MB < 512MB hard limit)

**Step 3: Exceed Hard Limit**
1. Create new revision
2. Change command: `--vm 1 --vm-bytes 600M --vm-hang 0`
3. Run task
4. Task will fail with OOMKilled error

#### Part D: Monitor Memory Usage

**Step 1: Set Up CloudWatch Alarm**
1. Go to CloudWatch → Alarms
2. Click "Create alarm"
3. Select metric:
   - ECS → ClusterName, ServiceName
   - Metric: MemoryUtilization
4. Conditions:
   - Threshold: Greater than 80%
5. Create alarm

**Step 2: View Container Insights**
1. Go to CloudWatch → Container Insights
2. Select your cluster
3. View memory metrics:
   - Memory utilization
   - Memory reserved
   - Memory used

#### Part E: Fix Memory Issues

**Scenario**: Your service keeps crashing with OOMKilled

**Step 1: Check Logs**
1. Go to CloudWatch Logs
2. Find your log group
3. Look for error messages:
   - "OutOfMemoryError"
   - "Container killed"
   - "Exit code 137" (OOM kill signal)

**Step 2: Update Memory**
1. Create new task definition revision
2. Increase hard limit by 50%
3. Update service with new revision
4. Monitor deployment

**Step 3: Verify Fix**
1. Check service events
2. Ensure tasks stay running
3. Monitor memory usage in CloudWatch

### What You Learned
- ✓ Understanding memory limits
- ✓ Task vs container memory
- ✓ Diagnosing OOMKilled errors
- ✓ Updating memory configuration
- ✓ Monitoring with CloudWatch

### Practice Scenarios

**Scenario 1**: Task won't start
- Error: "Insufficient memory"
- Solution: Reduce soft limits or add more instances

**Scenario 2**: Container keeps restarting
- Error: "OOMKilled"
- Solution: Increase hard limit

**Scenario 3**: Tasks fail to place
- Error: "No container instances available"
- Solution: Check soft limits vs available memory

---

## Exercise 5: Accessing and Debugging Containers

### Objective
Learn different methods to access and debug containers.

### Scenario
Your application is misbehaving. You need to access it for debugging.

### Step-by-Step Instructions

#### Part A: Enable ECS Exec for Fargate

**Step 1: Update Task Role**
1. Go to IAM → Roles
2. Find your task role (or create new)
3. Attach policy: `AmazonSSMManagedInstanceCore`

**Step 2: Update Task Definition**
1. Create new revision
2. Set task role to the role from Step 1
3. Create revision

**Step 3: Enable ECS Exec on Service**
1. Go to your service
2. Click "Update"
3. Check "Enable Execute Command"
4. Force new deployment
5. Update service

**Step 4: Install Session Manager Plugin**
Follow AWS documentation for your OS:
- Windows: Download and install MSI
- Mac: Use brew or download
- Linux: Use package manager

**Step 5: Connect to Container**
```bash
# Get task ID
aws ecs list-tasks --cluster my-first-cluster --service-name my-web-service

# Connect
aws ecs execute-command \
    --cluster my-first-cluster \
    --task <task-id> \
    --container nginx \
    --interactive \
    --command "/bin/bash"
```

#### Part B: Debug Common Issues

**Scenario 1: Application Not Responding**

**Steps**:
1. Connect to container
2. Check if process is running:
```bash
ps aux
```
3. Check ports:
```bash
netstat -tulpn
```
4. Check logs:
```bash
tail -f /var/log/nginx/error.log
```

**Scenario 2: Configuration Issues**

**Steps**:
1. Connect to container
2. View configuration:
```bash
cat /etc/nginx/nginx.conf
```
3. Test configuration:
```bash
nginx -t
```
4. Check environment variables:
```bash
env
```

**Scenario 3: Network Issues**

**Steps**:
1. Connect to container
2. Test connectivity:
```bash
# Install tools if needed
apt-get update && apt-get install -y curl telnet

# Test external connectivity
curl https://www.google.com

# Test internal service
curl http://localhost:80

# Test DNS
nslookup google.com
```

#### Part C: Access EC2-Based Containers

**Step 1: SSH to EC2 Instance**
```bash
ssh -i your-key.pem ec2-user@<ec2-ip>
```

**Step 2: List Containers**
```bash
docker ps
```

**Step 3: Access Container**
```bash
docker exec -it <container-id> /bin/bash
```

**Step 4: View Container Logs**
```bash
# View logs
docker logs <container-id>

# Follow logs
docker logs -f <container-id>

# Last 100 lines
docker logs --tail 100 <container-id>
```

**Step 5: Inspect Container**
```bash
# Full details
docker inspect <container-id>

# Just IP address
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container-id>

# Environment variables
docker inspect -f '{{.Config.Env}}' <container-id>
```

### What You Learned
- ✓ Enabled ECS Exec
- ✓ Connected to Fargate containers
- ✓ Debugged common issues
- ✓ Used Docker commands on EC2
- ✓ Inspected container details

---

## Exercise 6: Log Configuration and Troubleshooting

### Objective
Master CloudWatch Logs configuration and troubleshoot logging issues.

### Scenario
Your logs aren't appearing in CloudWatch. Learn to diagnose and fix.

### Step-by-Step Instructions

#### Part A: Proper Log Configuration

**Step 1: Create Task Definition with Logging**
1. Task definition family: `logging-test`
2. Add container:
   - Name: `app`
   - Image: `nginx:latest`
3. Log configuration:
   - Log driver: `awslogs`
   - Options:
     - awslogs-group: `/ecs/logging-test`
     - awslogs-region: `us-east-1` (your region)
     - awslogs-stream-prefix: `ecs`
     - awslogs-create-group: `true`

**Step 2: Verify Task Execution Role**
1. Go to IAM → Roles
2. Find task execution role
3. Ensure it has: `AmazonECSTaskExecutionRolePolicy`

#### Part B: Troubleshoot Missing Logs

**Scenario 1: No Log Group**

**Problem**: Logs don't appear, log group doesn't exist

**Solution**:
1. Go to CloudWatch → Log groups
2. Manually create log group: `/ecs/logging-test`
3. Or enable auto-create in task definition

**Scenario 2: Permission Denied**

**Problem**: Task fails to start, error about logs

**Solution**:
1. Check task execution role
2. Add CloudWatch Logs permissions:
```json
{
  "Effect": "Allow",
  "Action": [
    "logs:CreateLogGroup",
    "logs:CreateLogStream",
    "logs:PutLogEvents"
  ],
  "Resource": "*"
}
```

**Scenario 3: Logs Appear Late**

**Problem**: Logs take time to appear

**Explanation**: 
- CloudWatch batches logs
- May take 30-60 seconds
- This is normal behavior

**Solution**: Wait or use `docker logs` for real-time

#### Part C: Advanced Logging

**Step 1: Custom Log Format**
Create task definition with custom logging:
```json
{
  "logConfiguration": {
    "logDriver": "awslogs",
    "options": {
      "awslogs-group": "/ecs/my-app",
      "awslogs-region": "us-east-1",
      "awslogs-stream-prefix": "prod",
      "awslogs-datetime-format": "%Y-%m-%d %H:%M:%S"
    }
  }
}
```

**Step 2: Set Log Retention**
1. Go to CloudWatch → Log groups
2. Select your log group
3. Actions → Edit retention setting
4. Choose retention period (e.g., 7 days)
5. Save

**Step 3: Create Log Filters**
1. Open log group
2. Click "Create metric filter"
3. Filter pattern: `[ERROR]`
4. Test pattern
5. Create filter
6. Create alarm based on filter

#### Part D: View and Analyze Logs

**Method 1: CloudWatch Logs Insights**
1. Go to CloudWatch → Logs Insights
2. Select log group
3. Run query:
```
fields @timestamp, @message
| filter @message like /error/
| sort @timestamp desc
| limit 20
```

**Method 2: Live Tail**
1. Go to log group
2. Click "Live tail"
3. Start streaming
4. See logs in real-time

**Method 3: Download Logs**
1. Select log stream
2. Actions → Download
3. Save as text file

### What You Learned
- ✓ Configured CloudWatch Logs
- ✓ Troubleshot logging issues
- ✓ Set log retention
- ✓ Created log filters
- ✓ Used Logs Insights

---

## Real-World Scenarios and Solutions

### Scenario 1: High Traffic Application

**Situation**: Your application receives variable traffic throughout the day.

**Requirements**:
- Scale automatically based on load
- Minimize costs during low traffic
- Ensure availability during peaks

**Solution**:
1. Use Fargate for automatic scaling
2. Configure Service Auto Scaling:
   - Target tracking: CPU utilization 70%
   - Min tasks: 2
   - Max tasks: 10
3. Use Application Load Balancer
4. Enable health checks

**Steps**:
1. Create ALB
2. Create target group
3. Update service with ALB
4. Configure auto scaling policy
5. Test with load testing tool

### Scenario 2: Microservices Architecture

**Situation**: Multiple services need to communicate.

**Requirements**:
- Service discovery
- Internal communication
- Load balancing

**Solution**:
1. Use AWS Cloud Map for service discovery
2. Create namespace
3. Register services
4. Use service names for communication

**Steps**:
1. Create Cloud Map namespace
2. Enable service discovery in ECS service
3. Configure DNS records
4. Update application to use service names

### Scenario 3: Database Connection

**Situation**: Container needs to connect to RDS database.

**Requirements**:
- Secure connection
- No hardcoded credentials
- Proper network access

**Solution**:
1. Use AWS Secrets Manager for credentials
2. Configure security groups
3. Use task role for Secrets Manager access
4. Inject secrets as environment variables

**Steps**:
1. Store DB credentials in Secrets Manager
2. Update task definition:
   - Add task role with Secrets Manager permissions
   - Reference secrets in environment variables
3. Configure security groups:
   - Allow ECS security group to access RDS
4. Test connection

### Scenario 4: CI/CD Pipeline

**Situation**: Automate deployment on code changes.

**Requirements**:
- Build Docker image
- Push to ECR
- Update ECS service

**Solution**:
1. Use AWS CodePipeline
2. CodeBuild for Docker build
3. CodeDeploy for ECS deployment

**Steps**:
1. Create CodeBuild project
2. Create buildspec.yml
3. Create CodePipeline
4. Connect to source repository
5. Configure deployment to ECS

### Scenario 5: Cost Optimization

**Situation**: ECS costs are high.

**Analysis**:
- Check resource utilization
- Identify over-provisioned tasks
- Consider Spot instances

**Solutions**:
1. Right-size task memory and CPU
2. Use Fargate Spot for non-critical workloads
3. Use EC2 Spot instances for EC2 launch type
4. Implement auto-scaling
5. Set up cost alerts

**Steps**:
1. Review CloudWatch metrics
2. Identify underutilized resources
3. Update task definitions
4. Enable Fargate Spot
5. Monitor savings

---

## Practice Challenges

### Challenge 1: Deploy Three-Tier Application
**Goal**: Deploy web, app, and database tiers

**Requirements**:
- Frontend: nginx
- Backend: Node.js API
- Database: Redis
- All in separate services
- Services communicate via Service Discovery

### Challenge 2: Implement Blue-Green Deployment
**Goal**: Deploy new version without downtime

**Requirements**:
- Create two task definitions (blue and green)
- Use ALB for traffic routing
- Switch traffic gradually
- Rollback capability

### Challenge 3: Multi-Region Deployment
**Goal**: Deploy application in two regions

**Requirements**:
- Same application in us-east-1 and us-west-2
- Route 53 for DNS
- Health checks
- Automatic failover

### Challenge 4: Secure Application
**Goal**: Implement security best practices

**Requirements**:
- Private subnets for containers
- Secrets in Secrets Manager
- IAM roles with least privilege
- Enable CloudTrail logging
- Implement WAF rules

### Challenge 5: Monitoring and Alerting
**Goal**: Complete monitoring solution

**Requirements**:
- CloudWatch dashboards
- Alarms for CPU, memory, errors
- Log aggregation
- SNS notifications
- Automated responses

---

## Troubleshooting Checklist

### Task Won't Start
- [ ] Check task definition is valid
- [ ] Verify IAM roles have correct permissions
- [ ] Ensure sufficient cluster capacity
- [ ] Check security group rules
- [ ] Verify image exists in ECR
- [ ] Check CloudWatch Logs for errors

### Container Keeps Restarting
- [ ] Check memory limits
- [ ] Review application logs
- [ ] Verify health check configuration
- [ ] Check for OOMKilled errors
- [ ] Test application locally
- [ ] Review environment variables

### Can't Access Application
- [ ] Verify security group allows traffic
- [ ] Check public IP is assigned (Fargate)
- [ ] Verify port mappings
- [ ] Test from within VPC
- [ ] Check target group health
- [ ] Review route table configuration

### Logs Not Appearing
- [ ] Verify log configuration in task definition
- [ ] Check task execution role permissions
- [ ] Ensure log group exists
- [ ] Verify application logs to stdout
- [ ] Check CloudWatch Logs quota
- [ ] Wait 60 seconds for batch processing

### High Costs
- [ ] Review resource utilization
- [ ] Check for idle resources
- [ ] Consider Fargate Spot
- [ ] Implement auto-scaling
- [ ] Right-size tasks
- [ ] Set up cost alerts

---

## Additional Resources

### AWS Documentation
- ECS Developer Guide
- Fargate User Guide
- CloudWatch Logs Documentation
- IAM Best Practices

### Practice Tips
1. Start small, scale gradually
2. Always clean up resources
3. Use tags for organization
4. Document your configurations
5. Test in dev before production
6. Monitor costs regularly

### Next Steps
1. Complete all exercises in order
2. Try practice challenges
3. Build a real application
4. Implement CI/CD
5. Learn about ECS with EKS
6. Explore advanced features

---

*End of Practical Exercises*
