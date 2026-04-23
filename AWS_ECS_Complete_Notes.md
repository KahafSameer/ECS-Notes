# AWS ECS Complete Study Notes

## Table of Contents
1. Understanding AWS Compute Services
2. Lambda vs Fargate vs EC2 in ECS
3. ECS Task and Service Management
4. Container Connectivity
5. Memory Management in ECS
6. Troubleshooting and Logging
7. Practical Exercises

---

## 1. Understanding AWS Compute Services

### What is AWS ECS?
Amazon Elastic Container Service (ECS) is a container orchestration service that helps you run and manage Docker containers on AWS. Think of it as a manager that decides where and how to run your containerized applications.

### Key Components:
- **Cluster**: A logical grouping of tasks or services
- **Task Definition**: A blueprint that describes how to run your container (like a recipe)
- **Task**: A running instance of a task definition
- **Service**: Ensures a specified number of tasks are always running
- **Container**: The actual application running in an isolated environment

---

## 2. Lambda vs Fargate vs EC2 in ECS - Detailed Comparison

### AWS Lambda
**What it is**: Serverless compute service where you just upload code and AWS runs it.

**Characteristics**:
- No servers to manage at all
- Runs code in response to events (API calls, file uploads, etc.)
- Maximum execution time: 15 minutes
- Automatic scaling
- Pay only when code runs (per millisecond)
- Memory: 128 MB to 10 GB

**Best for**:
- Short-running tasks
- Event-driven applications
- Microservices with unpredictable traffic
- Background jobs

**Example Use Cases**:
- Image processing when uploaded to S3
- API backends with API Gateway
- Scheduled tasks (cron jobs)
- Data transformation

---

### AWS Fargate (Serverless Container Service)
**What it is**: Run containers without managing servers. AWS handles the infrastructure.

**Characteristics**:
- No EC2 instances to manage
- You define CPU and memory requirements
- AWS provisions the right compute resources
- Pay for resources your containers use
- Automatic scaling available
- No SSH access to underlying infrastructure
- Longer running tasks (no time limit like Lambda)

**Best for**:
- Containerized applications
- Microservices
- Batch processing jobs
- Applications that need to run continuously
- When you don't want to manage servers

**Example Use Cases**:
- Web applications
- API services
- Background processing workers
- Scheduled batch jobs

---

### EC2 Launch Type in ECS
**What it is**: Run containers on EC2 instances that YOU manage.

**Characteristics**:
- You manage the EC2 instances (servers)
- Full control over instance type, size, and configuration
- You can SSH into the instances
- More cost-effective for steady, predictable workloads
- You handle scaling, patching, and maintenance
- Can use Spot instances for cost savings
- Access to instance storage and GPU instances

**Best for**:
- Large-scale applications with steady traffic
- Applications needing specific instance types (GPU, high memory)
- Cost optimization for predictable workloads
- When you need full control over infrastructure
- Applications requiring persistent storage

**Example Use Cases**:
- Large production applications
- Machine learning workloads (GPU instances)
- Applications with compliance requirements
- High-performance computing

---

### Quick Comparison Table

| Feature | Lambda | Fargate | EC2 in ECS |
|---------|--------|---------|------------|
| Server Management | None | None | You manage |
| Execution Time | Max 15 minutes | Unlimited | Unlimited |
| SSH Access | No | No | Yes |
| Scaling | Automatic | Automatic/Manual | Manual/Auto Scaling |
| Cost Model | Per invocation | Per task resources | Per instance hour |
| Cold Start | Yes | Yes (minimal) | No |
| Container Support | Limited | Full Docker | Full Docker |
| Control Level | Low | Medium | High |
| Setup Complexity | Lowest | Medium | Highest |

---

## 3. ECS Task and Service Management

### Can We Log In to a Task in a Service?

**Short Answer**: 
- **Fargate**: No direct SSH, but you can use ECS Exec
- **EC2 Launch Type**: Yes, you can SSH to the EC2 instance and access containers

### Fargate SSH - Is It Possible?

**Traditional SSH**: No, Fargate doesn't allow SSH access because you don't have access to the underlying infrastructure.

**Alternative - ECS Exec**: Yes! AWS provides ECS Exec feature to access running containers.

#### How ECS Exec Works:
1. Uses AWS Systems Manager (SSM) Session Manager
2. Provides secure shell access to containers
3. No need to open SSH ports
4. All sessions are logged in CloudWatch

#### Requirements for ECS Exec:
- Task role must have SSM permissions
- ECS Exec must be enabled on the service
- AWS CLI version 1.22.0 or higher
- Session Manager plugin installed

#### Steps to Enable ECS Exec (AWS Console Method):

**Step 1: Update Task Role**
1. Go to IAM Console
2. Find your task role
3. Attach policy: `AmazonSSMManagedInstanceCore`

**Step 2: Enable ECS Exec on Service**
1. Go to ECS Console
2. Select your cluster
3. Select your service
4. Click "Update"
5. Check "Enable Execute Command"
6. Update service

**Step 3: Connect to Container (Using AWS CLI)**
```bash
aws ecs execute-command \
    --cluster your-cluster-name \
    --task your-task-id \
    --container your-container-name \
    --interactive \
    --command "/bin/bash"
```

### Logging into EC2 Launch Type Tasks

**Method 1: SSH to EC2 Instance**
1. Go to EC2 Console
2. Find the ECS instance
3. Click "Connect"
4. Use EC2 Instance Connect or SSH with key pair

**Method 2: Access Container from EC2**
Once on the EC2 instance:
```bash
# List running containers
docker ps

# Access a specific container
docker exec -it <container-id> /bin/bash

# View container logs
docker logs <container-id>
```

---

## 4. How to Connect Containers in a Task

### Understanding Container Networking in ECS

When multiple containers are defined in the same task definition, they can communicate with each other easily.

### Connection Methods:

#### Method 1: Localhost Communication (Same Task)
Containers in the same task share the same network namespace and can communicate via `localhost`.

**Example Scenario**: 
- Container 1: Web application (port 3000)
- Container 2: Redis cache (port 6379)

**How they connect**:
- Web app connects to Redis using: `localhost:6379`
- Both containers can reach each other via localhost

**Task Definition Example**:
```json
{
  "family": "my-app",
  "containerDefinitions": [
    {
      "name": "web-app",
      "image": "my-web-app:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "REDIS_HOST",
          "value": "localhost"
        },
        {
          "name": "REDIS_PORT",
          "value": "6379"
        }
      ]
    },
    {
      "name": "redis",
      "image": "redis:latest",
      "portMappings": [
        {
          "containerPort": 6379,
          "protocol": "tcp"
        }
      ]
    }
  ]
}
```

#### Method 2: Service Discovery (Different Tasks)
For containers in different tasks, use AWS Cloud Map (Service Discovery).

**How it works**:
1. Create a namespace (like a phone book)
2. Register services with names
3. Containers can connect using service names instead of IP addresses

**Example**:
- Service name: `backend.local`
- Containers connect to: `http://backend.local:8080`

#### Method 3: Load Balancer
Use Application Load Balancer (ALB) to route traffic between services.

---

## 5. Memory Management in ECS - Detailed Explanation

### Understanding Memory Types

#### 1. Container Memory
Memory allocated to individual containers within a task.

**Two Types of Limits**:

**Soft Limit (memoryReservation)**:
- Minimum memory guaranteed to the container
- Container can use more if available
- Think of it as "reserved parking spot"
- ECS uses this for task placement decisions

**Hard Limit (memory)**:
- Maximum memory the container can use
- If exceeded, container is killed (OOMKilled - Out Of Memory Killed)
- Think of it as "absolute ceiling"
- Protects other containers from memory hogging

#### 2. Task Memory
Total memory allocated to the entire task (all containers combined).

**For Fargate**: You must specify task-level memory (required)
**For EC2**: Optional, but recommended

### Memory Configuration Examples

#### Example 1: Single Container
```json
{
  "containerDefinitions": [
    {
      "name": "app",
      "memory": 512,           // Hard limit: 512 MB
      "memoryReservation": 256  // Soft limit: 256 MB
    }
  ],
  "memory": "512"  // Task memory (Fargate requires this)
}
```

#### Example 2: Multiple Containers
```json
{
  "containerDefinitions": [
    {
      "name": "web",
      "memory": 512,
      "memoryReservation": 256
    },
    {
      "name": "sidecar",
      "memory": 256,
      "memoryReservation": 128
    }
  ],
  "memory": "1024"  // Total task memory
}
```

### Can We Change Memory If We Face Issues?

**Yes, but with conditions**:

#### For Running Tasks:
**No** - You cannot change memory for already running tasks.

#### Solution - Update and Redeploy:
1. Update the task definition with new memory values
2. Create a new revision
3. Update the service to use the new revision
4. ECS will perform a rolling deployment

#### Steps in AWS Console:

**Step 1: Create New Task Definition Revision**
1. Go to ECS Console → Task Definitions
2. Select your task definition
3. Click "Create new revision"
4. Scroll to container definitions
5. Click on container name
6. Update memory values:
   - Hard limit (Memory)
   - Soft limit (Memory Reservation)
7. Click "Update"
8. Click "Create"

**Step 2: Update Service**
1. Go to your cluster
2. Select the service
3. Click "Update"
4. Select the new task definition revision
5. Choose deployment configuration:
   - Rolling update (recommended)
   - Minimum healthy percent: 100
   - Maximum percent: 200
6. Click "Update"

**Step 3: Monitor Deployment**
1. Watch the "Deployments" tab
2. Old tasks will be stopped
3. New tasks with updated memory will start

---

### What Happens When Memory Limits Are Exceeded?

#### Scenario 1: Soft Limit Exceeded (memoryReservation)
**What happens**:
- Container continues running
- Can use more memory if available on the host
- No immediate impact
- May affect task placement for new tasks

**Impact on Deployment**:
- No impact on running containers
- ECS may struggle to place new tasks if host memory is tight

#### Scenario 2: Hard Limit Exceeded (memory)
**What happens**:
- Container is immediately killed (OOMKilled)
- ECS tries to restart the container
- If it keeps failing, task stops
- Service will try to start a new task

**Impact on Deployment**:
- Service disruption
- Failed health checks
- Deployment may fail if new tasks keep crashing
- Application downtime

**Error Messages You'll See**:
```
Essential container in task exited
OutOfMemoryError: Container killed due to memory usage
Status: STOPPED, Reason: Essential container exited
```

#### Scenario 3: Task Memory Exceeded (Fargate)
**What happens**:
- Entire task is killed
- All containers in the task stop
- Service starts a new task

**Impact**:
- More severe than single container failure
- All containers in task affected
- Longer recovery time

---

### Which Memory Issue Causes Problems?

#### Problem 1: Hard Limit Too Low
**Symptoms**:
- Containers keep restarting
- OOMKilled errors in logs
- Service can't maintain desired count

**Solution**:
- Increase hard limit (memory)
- Optimize application memory usage
- Check for memory leaks

#### Problem 2: Soft Limit Too High
**Symptoms**:
- Tasks fail to place on EC2 instances
- "Insufficient memory" errors
- Cluster appears to have capacity but tasks won't start

**Solution**:
- Reduce soft limit (memoryReservation)
- Add more EC2 instances
- Use larger instance types

#### Problem 3: Task Memory Too Low (Fargate)
**Symptoms**:
- Task fails to start
- Error: "Container memory + overhead exceeds task memory"

**Solution**:
- Increase task-level memory
- Ensure: Task Memory ≥ Sum of all container hard limits

---

### Memory Best Practices

1. **Start Conservative**: Begin with lower values and increase based on monitoring

2. **Monitor Usage**: Use CloudWatch Container Insights
   - Track memory utilization
   - Set alarms for high memory usage (>80%)

3. **Set Both Limits**:
   - Soft limit: 50-70% of expected usage
   - Hard limit: 20-30% above soft limit

4. **Leave Headroom**: Don't use 100% of available memory

5. **Test Under Load**: Simulate production traffic to find right values

---

## 6. EC2 Launch Type - Infrastructure and Visibility

### Understanding EC2 in ECS

When you use EC2 launch type, you have full visibility and control over the infrastructure.

### What You Can See and Access:

#### 1. EC2 Instances
- View all instances in EC2 console
- See instance type, size, and specifications
- Monitor CPU, memory, disk usage
- Access instance metadata

#### 2. ECS Agent
- Software running on each EC2 instance
- Communicates with ECS service
- Manages container lifecycle
- Reports instance status

#### 3. Docker Containers
- All containers running on the instance
- Container logs and metrics
- Resource usage per container

#### 4. Network Configuration
- Security groups
- VPC settings
- Subnet placement
- Elastic Network Interfaces (ENIs)

### How to Explore EC2 in ECS Infrastructure

#### Step 1: View ECS Container Instances
1. Go to ECS Console
2. Select your cluster
3. Click "ECS Instances" tab
4. You'll see:
   - Instance ID
   - EC2 instance type
   - Running tasks count
   - CPU and memory availability
   - Agent version

#### Step 2: Access EC2 Instance Details
1. Click on an instance ID
2. This takes you to EC2 console
3. View:
   - Instance state
   - Public/Private IP
   - Security groups
   - IAM role
   - Monitoring metrics

#### Step 3: Connect to Instance
1. Select the instance
2. Click "Connect"
3. Choose connection method:
   - EC2 Instance Connect (browser-based)
   - Session Manager (no SSH key needed)
   - SSH (requires key pair)

#### Step 4: Explore Containers on Instance
Once connected:
```bash
# Check ECS agent status
sudo systemctl status ecs

# List running containers
docker ps

# View all containers (including stopped)
docker ps -a

# Check container resource usage
docker stats

# View container logs
docker logs <container-id>

# Inspect container details
docker inspect <container-id>

# Check available disk space
df -h

# Check memory usage
free -m

# Check CPU usage
top
```

---

### Connection, Login, and Restrictions in ECS Instances

#### Enabling SSH Access to ECS Instances

**Requirements**:
1. Security group must allow SSH (port 22)
2. Instance must have public IP (for internet access)
3. You need the SSH key pair

**Steps to Enable SSH**:

**Step 1: Configure Security Group**
1. Go to EC2 Console → Security Groups
2. Find the security group attached to ECS instances
3. Click "Edit inbound rules"
4. Add rule:
   - Type: SSH
   - Protocol: TCP
   - Port: 22
   - Source: Your IP address (for security)
5. Save rules

**Step 2: Ensure Instance Has Public IP**
1. Check instance details
2. If no public IP:
   - Allocate Elastic IP
   - Associate with instance

**Step 3: Connect via SSH**
```bash
ssh -i /path/to/your-key.pem ec2-user@<instance-public-ip>
```

#### Using Session Manager (No SSH Key Required)

**Advantages**:
- No need to open port 22
- No SSH keys to manage
- All sessions logged
- Works with private instances

**Requirements**:
1. SSM Agent installed (pre-installed on Amazon Linux 2)
2. Instance role has SSM permissions
3. Session Manager plugin on your computer

**Steps**:

**Step 1: Update Instance IAM Role**
1. Go to IAM Console
2. Find the instance role (usually named like `ecsInstanceRole`)
3. Attach policy: `AmazonSSMManagedInstanceCore`

**Step 2: Connect via Console**
1. Go to EC2 Console
2. Select instance
3. Click "Connect"
4. Choose "Session Manager" tab
5. Click "Connect"

#### Restricting Access to ECS Instances

**Best Practices**:

1. **Use Private Subnets**:
   - Place ECS instances in private subnets
   - No direct internet access
   - Access via bastion host or VPN

2. **Limit Security Group Rules**:
   - Only allow necessary ports
   - Restrict SSH to specific IP ranges
   - Use security group references

3. **Use IAM Roles**:
   - Don't store credentials on instances
   - Use instance roles for AWS API access
   - Rotate credentials regularly

4. **Enable CloudTrail**:
   - Log all API calls
   - Monitor access patterns
   - Set up alerts for suspicious activity

5. **Use Session Manager Instead of SSH**:
   - Better security
   - Centralized logging
   - No key management

---

## 7. Troubleshooting - If Logs Do Not Appear

### Common Reasons Logs Don't Appear

#### Reason 1: CloudWatch Logs Not Configured

**Problem**: Task definition doesn't have log configuration.

**Solution - Configure in Task Definition**:

**Steps in AWS Console**:
1. Go to ECS → Task Definitions
2. Create new revision
3. Scroll to container definition
4. Expand "Log configuration"
5. Select "awslogs" as log driver
6. Configure:
   - Log group: `/ecs/your-app-name`
   - Region: Your AWS region
   - Stream prefix: `ecs`
7. Check "Auto-configure CloudWatch Logs"
8. Save and create new revision

**JSON Example**:
```json
{
  "logConfiguration": {
    "logDriver": "awslogs",
    "options": {
      "awslogs-group": "/ecs/my-app",
      "awslogs-region": "us-east-1",
      "awslogs-stream-prefix": "ecs",
      "awslogs-create-group": "true"
    }
  }
}
```

#### Reason 2: Missing IAM Permissions

**Problem**: Task execution role lacks CloudWatch Logs permissions.

**Solution**:

**Steps**:
1. Go to IAM Console
2. Find your task execution role
3. Ensure it has policy: `AmazonECSTaskExecutionRolePolicy`
4. Or add custom policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

#### Reason 3: Log Group Doesn't Exist

**Problem**: CloudWatch log group not created.

**Solution**:

**Option 1: Auto-create (Recommended)**
- Set `awslogs-create-group: true` in task definition

**Option 2: Manual Creation**
1. Go to CloudWatch Console
2. Click "Log groups"
3. Click "Create log group"
4. Name: `/ecs/your-app-name`
5. Set retention period (e.g., 7 days)
6. Create

#### Reason 4: Application Not Writing to stdout/stderr

**Problem**: Application writes logs to files instead of console.

**Solution**: Configure application to log to stdout/stderr

**For Node.js**:
```javascript
console.log("This will appear in CloudWatch");
```

**For Python**:
```python
import logging
logging.basicConfig(level=logging.INFO)
logging.info("This will appear in CloudWatch")
```

**For Java**:
```java
System.out.println("This will appear in CloudWatch");
```

#### Reason 5: Container Exits Too Quickly

**Problem**: Container crashes before logs are sent.

**Solution**:
1. Check container exit code
2. View stopped task details
3. Look for error messages
4. Fix application issue

### How to View Logs

#### Method 1: CloudWatch Console
1. Go to CloudWatch Console
2. Click "Log groups"
3. Find your log group: `/ecs/your-app-name`
4. Click on log stream
5. View logs

#### Method 2: ECS Console
1. Go to ECS Console
2. Select cluster → Service → Tasks
3. Click on a task
4. Scroll to "Logs" tab
5. View logs directly

#### Method 3: AWS CLI
```bash
# List log streams
aws logs describe-log-streams \
    --log-group-name /ecs/my-app

# View logs
aws logs tail /ecs/my-app --follow
```

#### Method 4: On EC2 Instance (EC2 Launch Type)
```bash
# SSH to instance
ssh -i key.pem ec2-user@instance-ip

# View container logs
docker logs <container-id>

# Follow logs in real-time
docker logs -f <container-id>
```

---

## 8. Summary and Quick Reference

### Key Takeaways

1. **Lambda**: For short, event-driven functions (max 15 min)
2. **Fargate**: For containers without server management
3. **EC2 in ECS**: For full control and cost optimization

### Memory Management Rules
- **Soft Limit**: Minimum guaranteed, can exceed
- **Hard Limit**: Maximum allowed, kills container if exceeded
- **Task Memory**: Must be ≥ sum of container hard limits

### Access Methods
- **Fargate**: Use ECS Exec (no SSH)
- **EC2**: SSH to instance, then docker exec

### Container Communication
- **Same Task**: Use localhost
- **Different Tasks**: Use Service Discovery or Load Balancer

### Troubleshooting Checklist
- ✓ Log configuration in task definition
- ✓ IAM permissions for CloudWatch Logs
- ✓ Log group exists
- ✓ Application logs to stdout/stderr
- ✓ Container runs long enough to send logs

---

## Important AWS Console Paths

### ECS Console
- Clusters: ECS → Clusters
- Task Definitions: ECS → Task Definitions
- Services: ECS → Clusters → [Your Cluster] → Services

### CloudWatch Console
- Logs: CloudWatch → Logs → Log groups
- Metrics: CloudWatch → Metrics → ECS

### IAM Console
- Roles: IAM → Roles
- Policies: IAM → Policies

### EC2 Console
- Instances: EC2 → Instances
- Security Groups: EC2 → Security Groups

---

*End of Notes*
